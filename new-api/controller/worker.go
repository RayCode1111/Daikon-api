package controller

import (
	"fmt"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/QuantumNous/new-api/common"
	"github.com/QuantumNous/new-api/constant"
	"github.com/QuantumNous/new-api/model"
	"github.com/gin-gonic/gin"
)

type WorkerRegistrationRequest struct {
	WorkerID    string `json:"worker_id"`
	ModelName   string `json:"model_name"`
	EndpointURL string `json:"endpoint_url"`
	Secret      string `json:"secret"`
	GPUInfo     string `json:"gpu_info"`
}

type WorkerHeartbeatRequest struct {
	WorkerID string `json:"worker_id"`
	Secret   string `json:"secret"`
}

type WorkerInfo struct {
	WorkerID      string    `json:"worker_id"`
	ModelName     string    `json:"model_name"`
	EndpointURL   string    `json:"endpoint_url"`
	LastHeartbeat time.Time `json:"last_heartbeat"`
	Status        string    `json:"status"` // "ONLINE", "STARTING", "OFFLINE"
	GPUInfo       string    `json:"gpu_info"`
	ChannelID     int       `json:"channel_id"`
}

var (
	activeWorkerMutex sync.RWMutex
	activeWorker      *WorkerInfo
)

func getWorkerSecret() string {
	secret := os.Getenv("WORKER_SECRET")
	if secret == "" {
		return "colab-worker-secret-key-123"
	}
	return secret
}

const DefaultColabChannelName = "Colab-Worker-Qwen2.5-7B"

func RegisterWorker(c *gin.Context) {
	var req WorkerRegistrationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "message": "invalid request payload: " + err.Error()})
		return
	}

	if req.Secret != getWorkerSecret() {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "message": "invalid worker secret"})
		return
	}

	if req.EndpointURL == "" || req.WorkerID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "message": "worker_id and endpoint_url are required"})
		return
	}

	req.EndpointURL = strings.TrimSuffix(req.EndpointURL, "/")

	modelNames := "qwen2.5-7b,qwen2.5-7b-instruct,Qwen/Qwen2.5-7B-Instruct-AWQ"
	if req.ModelName != "" {
		if !strings.Contains(modelNames, req.ModelName) {
			modelNames = req.ModelName + "," + modelNames
		}
	}

	// Find or create Channel in New-API
	var channel model.Channel
	err := model.DB.Where("name = ?", DefaultColabChannelName).First(&channel).Error

	baseURL := req.EndpointURL
	weight := uint(1)
	priority := int64(100)
	autoBan := 0

	modelMapping := `{"Qwen/Qwen2.5-7B-Instruct-AWQ": "qwen2.5-7b", "qwen2.5-7b-instruct": "qwen2.5-7b"}`

	if err != nil {
		// Create new channel
		channel = model.Channel{
			Type:         constant.ChannelTypeOpenAI,
			Name:         DefaultColabChannelName,
			Key:          "dummy-worker-key",
			BaseURL:      &baseURL,
			Models:       modelNames,
			ModelMapping: &modelMapping,
			Group:        "default",
			Status:       common.ChannelStatusEnabled,
			Weight:       &weight,
			Priority:     &priority,
			AutoBan:      &autoBan,
			CreatedTime:  common.GetTimestamp(),
		}
		if err := channel.Insert(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"success": false, "message": "failed to insert channel: " + err.Error()})
			return
		}
	} else {
		// Update existing channel
		channel.BaseURL = &baseURL
		channel.Status = common.ChannelStatusEnabled
		channel.Models = modelNames
		channel.ModelMapping = &modelMapping
		channel.Type = constant.ChannelTypeOpenAI
		if err := channel.Update(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"success": false, "message": "failed to update channel: " + err.Error()})
			return
		}
	}

	model.InitChannelCache()

	activeWorkerMutex.Lock()
	activeWorker = &WorkerInfo{
		WorkerID:      req.WorkerID,
		ModelName:     req.ModelName,
		EndpointURL:   req.EndpointURL,
		LastHeartbeat: time.Now(),
		Status:        "ONLINE",
		GPUInfo:       req.GPUInfo,
		ChannelID:     channel.Id,
	}
	activeWorkerMutex.Unlock()

	common.SysLog(fmt.Sprintf("[Worker] Worker '%s' registered with endpoint '%s'. Model '%s' is now ONLINE.", req.WorkerID, req.EndpointURL, req.ModelName))

	c.JSON(http.StatusOK, gin.H{
		"success":    true,
		"message":    "Worker successfully registered and model is ONLINE",
		"channel_id": channel.Id,
		"status":     "ONLINE",
	})
}

func HeartbeatWorker(c *gin.Context) {
	var req WorkerHeartbeatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "message": "invalid request payload"})
		return
	}

	if req.Secret != getWorkerSecret() {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "message": "invalid worker secret"})
		return
	}

	activeWorkerMutex.Lock()
	defer activeWorkerMutex.Unlock()

	if activeWorker == nil || activeWorker.WorkerID != req.WorkerID {
		c.JSON(http.StatusNotFound, gin.H{"success": false, "message": "worker not registered or session mismatch"})
		return
	}

	activeWorker.LastHeartbeat = time.Now()
	if activeWorker.Status != "ONLINE" {
		activeWorker.Status = "ONLINE"
		// Re-enable channel if it was disabled
		var channel model.Channel
		if err := model.DB.First(&channel, "id = ?", activeWorker.ChannelID).Error; err == nil {
			channel.Status = common.ChannelStatusEnabled
			_ = channel.Update()
			model.InitChannelCache()
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"status":  "healthy",
	})
}

func DeregisterWorker(c *gin.Context) {
	var req WorkerHeartbeatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "message": "invalid request payload"})
		return
	}

	if req.Secret != getWorkerSecret() {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "message": "invalid worker secret"})
		return
	}

	activeWorkerMutex.Lock()
	defer activeWorkerMutex.Unlock()

	if activeWorker != nil {
		var channel model.Channel
		if err := model.DB.First(&channel, "id = ?", activeWorker.ChannelID).Error; err == nil {
			channel.Status = common.ChannelStatusManuallyDisabled
			_ = channel.Update()
			model.InitChannelCache()
		}
		activeWorker.Status = "OFFLINE"
		common.SysLog(fmt.Sprintf("[Worker] Worker '%s' gracefully deregistered. Model set to OFFLINE.", activeWorker.WorkerID))
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Worker deregistered and channel disabled",
	})
}

func GetWorkerStatus(c *gin.Context) {
	activeWorkerMutex.RLock()
	defer activeWorkerMutex.RUnlock()

	if activeWorker == nil {
		c.JSON(http.StatusOK, gin.H{
			"model":          "qwen2.5-7b",
			"status":         "OFFLINE",
			"message":        "No worker currently connected. Launch Google Colab notebook to activate.",
			"last_heartbeat": 0,
		})
		return
	}

	secondsSinceLast := int(time.Since(activeWorker.LastHeartbeat).Seconds())

	c.JSON(http.StatusOK, gin.H{
		"worker_id":           activeWorker.WorkerID,
		"model":               activeWorker.ModelName,
		"status":              activeWorker.Status,
		"endpoint_url":        activeWorker.EndpointURL,
		"gpu_info":            activeWorker.GPUInfo,
		"last_heartbeat_secs": secondsSinceLast,
	})
}

func StartWorkerHeartbeatWatcher() {
	go func() {
		ticker := time.NewTicker(10 * time.Second)
		defer ticker.Stop()

		for range ticker.C {
			activeWorkerMutex.Lock()
			if activeWorker != nil && activeWorker.Status == "ONLINE" {
				if time.Since(activeWorker.LastHeartbeat) > 45*time.Second {
					activeWorker.Status = "OFFLINE"
					common.SysLog(fmt.Sprintf("[Worker Watcher] Heartbeat expired for worker '%s' (%v since last ping). Marking channel %d OFFLINE.",
						activeWorker.WorkerID, time.Since(activeWorker.LastHeartbeat), activeWorker.ChannelID))

					var channel model.Channel
					if err := model.DB.First(&channel, "id = ?", activeWorker.ChannelID).Error; err == nil {
						channel.Status = common.ChannelStatusAutoDisabled
						_ = channel.Update()
						model.InitChannelCache()
					}
				}
			}
			activeWorkerMutex.Unlock()
		}
	}()
}

