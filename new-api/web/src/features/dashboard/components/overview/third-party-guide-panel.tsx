import { Laptop, Terminal, Sparkles, Code2, Globe, ExternalLink, KeyRound } from 'lucide-react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { CopyButton } from '@/components/copy-button'
import type { ApiKey } from '@/features/keys/types'

interface ThirdPartyGuidePanelProps {
  apiKeys?: ApiKey[]
}

export function ThirdPartyGuidePanel(_props: ThirdPartyGuidePanelProps) {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState('curl')

  const origin = typeof window !== 'undefined' ? window.location.origin : 'https://daikon-api.onrender.com'
  const baseUrl = `${origin}/v1`
  const modelName = 'Qwen/Qwen2.5-7B-Instruct-AWQ'
  const apiKeyPlaceholder = 'Your Daikon API key here'

  const curlSnippet = `curl ${baseUrl}/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${apiKeyPlaceholder}" \\
  -d '{
    "model": "${modelName}",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello! How can you help me today?"}
    ],
    "temperature": 0.7
  }'`

  const pythonSnippet = `from openai import OpenAI

client = OpenAI(
    base_url="${baseUrl}",
    api_key="${apiKeyPlaceholder}",
)

completion = client.chat.completions.create(
    model="${modelName}",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Explain quantum computing simply."}
    ],
)

print(completion.choices[0].message.content)`

  const nodeSnippet = `import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: '${baseUrl}',
  apiKey: '${apiKeyPlaceholder}',
});

async function main() {
  const completion = await client.chat.completions.create({
    model: '${modelName}',
    messages: [
      { role: 'system', content: 'You are a helpful assistant.' },
      { role: 'user', content: 'Hello from Daikon API!' }
    ],
  });

  console.log(completion.choices[0].message.content);
}

main();`

  return (
    <Card className='border shadow-sm overflow-hidden rounded-2xl'>
      <CardHeader className='pb-3'>
        <div className='flex flex-wrap items-center justify-between gap-3'>
          <div className='flex items-center gap-2.5'>
            <div className='bg-primary/10 text-primary flex size-9 items-center justify-center rounded-xl'>
              <Sparkles className='size-5' />
            </div>
            <div>
              <CardTitle className='text-lg font-semibold tracking-tight'>
                {t('Setup & First API Request')}
              </CardTitle>
              <CardDescription className='text-xs'>
                {t('Connect Daikon API with NextChat, Cherry Studio, ChatBox, or your own code. Powered by free Qwen 2.5 7B.')}
              </CardDescription>
            </div>
          </div>
          <div className='flex items-center gap-2'>
            <Button size='sm' variant='outline' render={<Link to='/keys' />}>
              <KeyRound className='size-3.5 mr-1.5' />
              {t('Manage API Keys')}
            </Button>
            <Button size='sm' render={<Link to='/playground' />}>
              {t('Test in Playground')}
            </Button>
          </div>
        </div>

        {/* Global Connection Parameters Bar */}
        <div className='mt-3 grid grid-cols-1 sm:grid-cols-3 gap-2.5 rounded-xl border bg-muted/40 p-3 text-xs'>
          <div className='flex flex-col gap-1 min-w-0'>
            <span className='text-muted-foreground font-medium'>{t('Base URL (API Host)')}</span>
            <div className='flex items-center justify-between gap-1 rounded-lg border bg-background/80 px-2 py-1 font-mono text-[11px]'>
              <span className='truncate'>{baseUrl}</span>
              <CopyButton value={baseUrl} className='size-5' iconClassName='size-3' />
            </div>
          </div>

          <div className='flex flex-col gap-1 min-w-0'>
            <div className='flex items-center gap-1.5'>
              <span className='text-muted-foreground font-medium'>{t('Active Model')}</span>
              <span className='rounded bg-emerald-500/15 px-1 py-0.2 font-mono text-[9px] font-bold text-emerald-500 border border-emerald-500/30'>
                100% FREE
              </span>
            </div>
            <div className='flex items-center justify-between gap-1 rounded-lg border bg-background/80 px-2 py-1 font-mono text-[11px]'>
              <span className='truncate'>{modelName}</span>
              <CopyButton value={modelName} className='size-5' iconClassName='size-3' />
            </div>
          </div>

          <div className='flex flex-col gap-1 min-w-0'>
            <span className='text-muted-foreground font-medium'>{t('Your API Key')}</span>
            <div className='flex items-center justify-between gap-1 rounded-lg border bg-background/80 px-2 py-1 font-mono text-[11px]'>
              <span className='truncate text-muted-foreground italic'>{apiKeyPlaceholder}</span>
              <Button size='sm' variant='ghost' className='h-5 px-1.5 text-[10px]' render={<Link to='/keys' />}>
                {t('Get Key')}
              </Button>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className='pt-1'>
        <Tabs value={activeTab} onValueChange={setActiveTab} className='w-full'>
          <TabsList className='bg-muted/70 flex h-auto flex-wrap justify-start gap-1 p-1'>
            <TabsTrigger value='curl' className='text-xs gap-1.5'>
              <Terminal className='size-3.5' />
              cURL (First Request)
            </TabsTrigger>
            <TabsTrigger value='python' className='text-xs gap-1.5'>
              <Code2 className='size-3.5' />
              Python (OpenAI SDK)
            </TabsTrigger>
            <TabsTrigger value='nextchat' className='text-xs gap-1.5'>
              <Laptop className='size-3.5' />
              NextChat
            </TabsTrigger>
            <TabsTrigger value='cherrystudio' className='text-xs gap-1.5'>
              <Laptop className='size-3.5' />
              Cherry Studio
            </TabsTrigger>
            <TabsTrigger value='chatbox' className='text-xs gap-1.5'>
              <Laptop className='size-3.5' />
              ChatBox
            </TabsTrigger>
            <TabsTrigger value='lobechat' className='text-xs gap-1.5'>
              <Globe className='size-3.5' />
              LobeChat
            </TabsTrigger>
            <TabsTrigger value='node' className='text-xs gap-1.5'>
              <Code2 className='size-3.5' />
              Node.js
            </TabsTrigger>
          </TabsList>

          {/* cURL Tutorial */}
          <TabsContent value='curl' className='mt-3 space-y-2'>
            <div className='flex items-center justify-between'>
              <p className='text-muted-foreground text-xs'>
                {t('Run this command in your terminal to send your first API request directly:')}
              </p>
              <CopyButton value={curlSnippet} variant='outline' size='sm' className='h-7 gap-1 text-xs px-2'>
                {t('Copy cURL')}
              </CopyButton>
            </div>
            <pre className='overflow-x-auto rounded-xl border bg-zinc-950 p-3 font-mono text-xs text-zinc-100 dark:bg-black'>
              <code>{curlSnippet}</code>
            </pre>
          </TabsContent>

          {/* Python Tutorial */}
          <TabsContent value='python' className='mt-3 space-y-2'>
            <div className='flex items-center justify-between'>
              <p className='text-muted-foreground text-xs'>
                {t('Install via')} <code className='rounded bg-muted px-1.5 py-0.5 font-mono text-[11px]'>pip install openai</code>
              </p>
              <CopyButton value={pythonSnippet} variant='outline' size='sm' className='h-7 gap-1 text-xs px-2'>
                {t('Copy Python')}
              </CopyButton>
            </div>
            <pre className='overflow-x-auto rounded-xl border bg-zinc-950 p-3 font-mono text-xs text-zinc-100 dark:bg-black'>
              <code>{pythonSnippet}</code>
            </pre>
          </TabsContent>

          {/* NextChat Guide */}
          <TabsContent value='nextchat' className='mt-3 space-y-3 text-xs'>
            <div className='rounded-xl border bg-muted/30 p-4 space-y-2.5'>
              <div className='font-semibold text-sm flex items-center gap-1.5'>
                <Laptop className='size-4 text-primary' />
                {t('How to configure NextChat (ChatGPT-Next-Web)')}
              </div>
              <ol className='list-decimal list-inside space-y-1.5 text-muted-foreground leading-relaxed'>
                <li>
                  {t('Open NextChat and click on the ')}
                  <strong className='text-foreground'>{t('Settings (gear icon)')}</strong>
                  {t(' in the bottom left corner.')}
                </li>
                <li>
                  {t('Under ')}
                  <strong className='text-foreground'>{t('Model Provider')}</strong>
                  {t(', select ')}
                  <strong className='text-foreground'>OpenAI</strong>.
                </li>
                <li>
                  {t('Set ')}
                  <strong className='text-foreground'>{t('OpenAI Endpoint')}</strong>
                  {t(' to: ')}
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground'>{baseUrl}</code>
                  <CopyButton value={baseUrl} className='size-5 inline-flex align-middle ml-1' iconClassName='size-3' />
                </li>
                <li>
                  {t('Set ')}
                  <strong className='text-foreground'>{t('API Key')}</strong>
                  {t(' to your Daikon key: ')}
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground'>{apiKeyPlaceholder}</code>
                </li>
                <li>
                  {t('In ')}
                  <strong className='text-foreground'>{t('Custom Models')}</strong>
                  {t(', add ')}
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground'>{modelName}</code>
                  <CopyButton value={modelName} className='size-5 inline-flex align-middle ml-1' iconClassName='size-3' />
                  {t(' and select it for your conversations.')}
                </li>
              </ol>
            </div>
          </TabsContent>

          {/* Cherry Studio Guide */}
          <TabsContent value='cherrystudio' className='mt-3 space-y-3 text-xs'>
            <div className='rounded-xl border bg-muted/30 p-4 space-y-2.5'>
              <div className='font-semibold text-sm flex items-center gap-1.5'>
                <Laptop className='size-4 text-primary' />
                {t('How to configure Cherry Studio')}
              </div>
              <ol className='list-decimal list-inside space-y-1.5 text-muted-foreground leading-relaxed'>
                <li>
                  {t('Open Cherry Studio, navigate to ')}
                  <strong className='text-foreground'>{t('Settings → Model Providers')}</strong>.
                </li>
                <li>
                  {t('Click ')}
                  <strong className='text-foreground'>{t('Add Provider')}</strong>
                  {t(' and choose ')}
                  <strong className='text-foreground'>OpenAI Compatible</strong>.
                </li>
                <li>
                  {t('Set ')}
                  <strong className='text-foreground'>{t('API URL / Base URL')}</strong>
                  {t(' to: ')}
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground'>{baseUrl}</code>
                  <CopyButton value={baseUrl} className='size-5 inline-flex align-middle ml-1' iconClassName='size-3' />
                </li>
                <li>
                  {t('Paste your ')}
                  <strong className='text-foreground'>{t('API Key')}</strong>:
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground ml-1'>{apiKeyPlaceholder}</code>
                </li>
                <li>
                  {t('Under Model Management, add Model ID: ')}
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground'>{modelName}</code>
                  <CopyButton value={modelName} className='size-5 inline-flex align-middle ml-1' iconClassName='size-3' />
                </li>
              </ol>
            </div>
          </TabsContent>

          {/* ChatBox Guide */}
          <TabsContent value='chatbox' className='mt-3 space-y-3 text-xs'>
            <div className='rounded-xl border bg-muted/30 p-4 space-y-2.5'>
              <div className='font-semibold text-sm flex items-center gap-1.5'>
                <Laptop className='size-4 text-primary' />
                {t('How to configure ChatBox')}
              </div>
              <ol className='list-decimal list-inside space-y-1.5 text-muted-foreground leading-relaxed'>
                <li>
                  {t('Open ChatBox and go to ')}
                  <strong className='text-foreground'>{t('Settings')}</strong>.
                </li>
                <li>
                  {t('Set ')}
                  <strong className='text-foreground'>{t('AI Provider')}</strong>
                  {t(' to ')}
                  <strong className='text-foreground'>OpenAI API</strong>.
                </li>
                <li>
                  {t('Set ')}
                  <strong className='text-foreground'>{t('API Host')}</strong>
                  {t(' to: ')}
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground'>{origin}</code>
                  <CopyButton value={origin} className='size-5 inline-flex align-middle ml-1' iconClassName='size-3' />
                  {t(' (or ')}<code className='font-mono'>{baseUrl}</code>{t(' if required)')}
                </li>
                <li>
                  {t('Enter your ')}
                  <strong className='text-foreground'>{t('API Key')}</strong>:
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground ml-1'>{apiKeyPlaceholder}</code>
                </li>
                <li>
                  {t('Set ')}
                  <strong className='text-foreground'>{t('Model')}</strong>
                  {t(' to: ')}
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground'>{modelName}</code>
                  <CopyButton value={modelName} className='size-5 inline-flex align-middle ml-1' iconClassName='size-3' />
                </li>
              </ol>
            </div>
          </TabsContent>

          {/* LobeChat Guide */}
          <TabsContent value='lobechat' className='mt-3 space-y-3 text-xs'>
            <div className='rounded-xl border bg-muted/30 p-4 space-y-2.5'>
              <div className='font-semibold text-sm flex items-center gap-1.5'>
                <Globe className='size-4 text-primary' />
                {t('How to configure LobeChat')}
              </div>
              <ol className='list-decimal list-inside space-y-1.5 text-muted-foreground leading-relaxed'>
                <li>
                  {t('Go to ')}
                  <strong className='text-foreground'>{t('Settings → Language Model → OpenAI')}</strong>.
                </li>
                <li>
                  {t('Enable the OpenAI provider toggle.')}
                </li>
                <li>
                  {t('Set ')}
                  <strong className='text-foreground'>{t('API Key')}</strong>:
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground ml-1'>{apiKeyPlaceholder}</code>
                </li>
                <li>
                  {t('Set ')}
                  <strong className='text-foreground'>{t('Endpoint (Base URL)')}</strong>
                  {t(' to: ')}
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground'>{baseUrl}</code>
                  <CopyButton value={baseUrl} className='size-5 inline-flex align-middle ml-1' iconClassName='size-3' />
                </li>
                <li>
                  {t('Add custom model: ')}
                  <code className='rounded bg-background px-1.5 py-0.5 font-mono text-foreground'>{modelName}</code>
                  <CopyButton value={modelName} className='size-5 inline-flex align-middle ml-1' iconClassName='size-3' />
                </li>
              </ol>
            </div>
          </TabsContent>

          {/* Node.js Tutorial */}
          <TabsContent value='node' className='mt-3 space-y-2'>
            <div className='flex items-center justify-between'>
              <p className='text-muted-foreground text-xs'>
                {t('Install via')} <code className='rounded bg-muted px-1.5 py-0.5 font-mono text-[11px]'>npm install openai</code>
              </p>
              <CopyButton value={nodeSnippet} variant='outline' size='sm' className='h-7 gap-1 text-xs px-2'>
                {t('Copy TypeScript')}
              </CopyButton>
            </div>
            <pre className='overflow-x-auto rounded-xl border bg-zinc-950 p-3 font-mono text-xs text-zinc-100 dark:bg-black'>
              <code>{nodeSnippet}</code>
            </pre>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
