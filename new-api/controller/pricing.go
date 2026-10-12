package controller

import (
	"maps"
	"strings"

	"github.com/QuantumNous/new-api/common"
	"github.com/QuantumNous/new-api/constant"
	"github.com/QuantumNous/new-api/model"
	"github.com/QuantumNous/new-api/service"
	"github.com/QuantumNous/new-api/setting/ratio_setting"

	"github.com/gin-gonic/gin"
)

func filterPricingByUsableGroups(pricing []model.Pricing, usableGroup map[string]string) []model.Pricing {
	if len(pricing) == 0 {
		return pricing
	}
	if len(usableGroup) == 0 {
		return []model.Pricing{}
	}

	filtered := make([]model.Pricing, 0, len(pricing))
	for _, item := range pricing {
		if common.StringsContains(item.EnableGroup, "all") {
			filtered = append(filtered, item)
			continue
		}
		for _, group := range item.EnableGroup {
			if _, ok := usableGroup[group]; ok {
				filtered = append(filtered, item)
				break
			}
		}
	}
	return filtered
}

func GetPricing(c *gin.Context) {
	rawPricing := model.GetPricing()
	userId, exists := c.Get("id")
	usableGroup := map[string]string{}
	groupRatio := map[string]float64{}
	maps.Copy(groupRatio, ratio_setting.GetGroupRatioCopy())
	var group string
	if exists {
		user, err := model.GetUserCache(userId.(int))
		if err == nil {
			group = user.Group
			for g := range groupRatio {
				ratio, ok := ratio_setting.GetGroupGroupRatio(group, g)
				if ok {
					groupRatio[g] = ratio
				}
			}
		}
	}

	usableGroup = service.GetUserUsableGroups(group)

	// Filter down raw pricing to only the active Qwen model
	var qwenPricing *model.Pricing
	for _, item := range rawPricing {
		nameLower := strings.ToLower(item.ModelName)
		if strings.Contains(nameLower, "qwen2.5-7b") || strings.Contains(nameLower, "qwen") {
			itemCopy := item
			itemCopy.ModelName = "Qwen/Qwen2.5-7B-Instruct-AWQ"
			itemCopy.ModelRatio = 0.0
			itemCopy.ModelPrice = 0.0
			itemCopy.CompletionRatio = 0.0
			itemCopy.QuotaType = 0
			itemCopy.VendorID = -1022
			itemCopy.Description = "High-performance open weights instruction model (4-bit AWQ quantized). Free to use."
			itemCopy.Tags = "Free, Chat, Featured"
			itemCopy.EnableGroup = []string{"default", "all"}
			itemCopy.SupportedEndpointTypes = []constant.EndpointType{constant.EndpointTypeOpenAI}
			qwenPricing = &itemCopy
			break
		}
	}

	if qwenPricing == nil {
		qwenPricing = &model.Pricing{
			ModelName:              "Qwen/Qwen2.5-7B-Instruct-AWQ",
			ModelRatio:             0.0,
			ModelPrice:             0.0,
			CompletionRatio:        0.0,
			QuotaType:              0,
			VendorID:               -1022,
			Description:            "High-performance open weights instruction model (4-bit AWQ quantized). Free to use.",
			Tags:                   "Free, Chat, Featured",
			EnableGroup:            []string{"default", "all"},
			SupportedEndpointTypes: []constant.EndpointType{constant.EndpointTypeOpenAI},
		}
	}

	// Curate final pricing list: 1 active free model + under development models
	curatedPricing := []model.Pricing{
		*qwenPricing,
		{
			ModelName:              "deepseek-v3 (Under Development)",
			VendorID:               -1005,
			Description:            "DeepSeek-V3 671B MoE architecture - Under development, coming soon.",
			Tags:                   "Under Development, Chat",
			ModelRatio:             0.0,
			ModelPrice:             0.0,
			QuotaType:              0,
			EnableGroup:            []string{"default", "all"},
			SupportedEndpointTypes: []constant.EndpointType{constant.EndpointTypeOpenAI},
		},
		{
			ModelName:              "gpt-4o (Under Development)",
			VendorID:               -1012,
			Description:            "OpenAI flagship multimodal intelligence - Under development, coming soon.",
			Tags:                   "Under Development, Chat",
			ModelRatio:             0.0,
			ModelPrice:             0.0,
			QuotaType:              0,
			EnableGroup:            []string{"default", "all"},
			SupportedEndpointTypes: []constant.EndpointType{constant.EndpointTypeOpenAI},
		},
		{
			ModelName:              "claude-3-5-sonnet (Under Development)",
			VendorID:               -1002,
			Description:            "Anthropic Claude 3.5 Sonnet - Under development, coming soon.",
			Tags:                   "Under Development, Chat",
			ModelRatio:             0.0,
			ModelPrice:             0.0,
			QuotaType:              0,
			EnableGroup:            []string{"default", "all"},
			SupportedEndpointTypes: []constant.EndpointType{constant.EndpointTypeOpenAI},
		},
	}

	pricing := filterPricingByUsableGroups(curatedPricing, usableGroup)

	// Clean groupRatio
	for groupKey := range ratio_setting.GetGroupRatioCopy() {
		if _, ok := usableGroup[groupKey]; !ok {
			delete(groupRatio, groupKey)
		}
	}

	vendors := []model.PricingVendor{
		{
			ID:          -1022,
			Name:        "Alibaba Cloud",
			Description: "Alibaba Cloud / Qwen open models",
			Icon:        "Qwen.Color",
		},
		{
			ID:          -1005,
			Name:        "DeepSeek",
			Description: "DeepSeek AI models",
			Icon:        "DeepSeek.Color",
		},
		{
			ID:          -1012,
			Name:        "OpenAI",
			Description: "OpenAI GPT models",
			Icon:        "OpenAI",
		},
		{
			ID:          -1002,
			Name:        "Anthropic",
			Description: "Anthropic Claude models",
			Icon:        "Claude.Color",
		},
	}

	c.JSON(200, gin.H{
		"success":            true,
		"data":               pricing,
		"vendors":            vendors,
		"group_ratio":        groupRatio,
		"usable_group":       usableGroup,
		"supported_endpoint": model.GetSupportedEndpointMap(),
		"auto_groups":        service.GetUserAutoGroup(group),
		"pricing_version":    "daikon-api-v1",
	})
}

func ResetModelRatio(c *gin.Context) {
	defaultStr := ratio_setting.DefaultModelRatio2JSONString()
	err := model.UpdateOption("ModelRatio", defaultStr)
	if err != nil {
		c.JSON(200, gin.H{
			"success": false,
			"message": err.Error(),
		})
		return
	}
	err = ratio_setting.UpdateModelRatioByJSONString(defaultStr)
	if err != nil {
		c.JSON(200, gin.H{
			"success": false,
			"message": err.Error(),
		})
		return
	}
	c.JSON(200, gin.H{
		"success": true,
		"message": "重置模型倍率成功",
	})
}
