<script>
  import { onMount } from 'svelte';
  import { writable, derived, get } from 'svelte/store';
  import { invoke } from '@tauri-apps/api/tauri';
  import { listen } from '@tauri-apps/api/event';
  import { open } from '@tauri-apps/api/dialog';
  

  // Consolidated state management for better performance
  /** @type {import('svelte/store').Writable<{directory: string, isProcessing: boolean, progress: number, logs: string[], config: {model: string, quality: number, lossless: boolean}, showSidebar: boolean, isTauriMode: boolean, tauriAvailable: boolean}>} */
  const appState = writable({
    directory: '',
    isProcessing: false,
    progress: 0,
    logs: [],
    config: {
      model: 'llava',
      quality: 85,
      lossless: false
    },
    showSidebar: true,
    mode: 'detecting', // 'desktop', 'web', 'detecting'
    tauriAvailable: false
  });

  // Derived stores for specific UI needs
  const isReady = derived(appState, $state => 
    $state.directory && !$state.isProcessing
  );
  
  // Virtual scrolling for logs - only show last 100 entries for performance
  const visibleLogs = derived(appState, $state => 
    $state.logs.length > 100 ? $state.logs.slice(-100) : $state.logs
  );

  onMount(async () => {
    // Enhanced Tauri detection and graceful fallback
    let tauriDetected = false;
    let cleanupFunctions = [];
    
    // Check if we're running in Tauri environment
    if (typeof window !== 'undefined' && window.__TAURI_METADATA__) {
      try {
        // Test Tauri API availability with a simple call
        await invoke('ping').catch(() => {
          // Even if ping fails, we might be in Tauri environment
          return null;
        });
        
        const unlisten = await listen('file-drop', (event) => {
          const paths = event.payload;
          if (paths.length > 0) {
            appState.update(state => ({
              ...state,
              directory: paths[0]
            }));
            addLog(`📁 Directory dropped: ${paths[0]}`);
          }
        });
        cleanupFunctions.push(unlisten);

        // Batched log processing for better performance
        let logBuffer = [];
        let isUpdatingLogs = false;
        
        const logUnlisten = await listen('log', (event) => {
          logBuffer.push(event.payload);
          
          if (!isUpdatingLogs) {
            isUpdatingLogs = true;
            requestAnimationFrame(() => {
              appState.update(state => ({
                ...state,
                logs: [...state.logs, ...logBuffer.splice(0)]
              }));
              isUpdatingLogs = false;
            });
          }
        });
        cleanupFunctions.push(logUnlisten);
        
        // Also listen for batched logs from optimized backend
        const batchLogUnlisten = await listen('logs_batch', (event) => {
          appState.update(state => ({
            ...state,
            logs: [...state.logs, ...event.payload]
          }));
        });
        cleanupFunctions.push(batchLogUnlisten);

        tauriDetected = true;
        appState.update(state => ({
          ...state,
          isTauriMode: true,
          tauriAvailable: true
        }));
        addLog('🖥️ Desktop mode: Full Tauri functionality enabled');
        
      } catch (error) {
        console.log('Tauri environment detected but APIs unavailable:', error);
        appState.update(state => ({
          ...state,
          isTauriMode: true,
          tauriAvailable: false
        }));
        addLog('⚠️ Desktop mode: Limited functionality (Tauri APIs unavailable)');
      }
    }
    
    if (!tauriDetected) {
      appState.update(state => ({
        ...state,
        isTauriMode: false,
        tauriAvailable: false
      }));
      addLog('🌐 Web mode: Browser-based functionality enabled');
    }

    return () => {
      cleanupFunctions.forEach(cleanup => cleanup());
    };
  });

  async function selectDirectory() {
    try {
      const selected = await open({ directory: true });
      if (selected) {
        appState.update(state => ({
          ...state,
          directory: selected
        }));
        addLog(`Directory selected: ${selected}`);
      }
    } catch (error) {
      // Fallback for web-only mode
      const fallbackPath = prompt('Enter directory path (web-only mode):');
      if (fallbackPath) {
        appState.update(state => ({
          ...state,
          directory: fallbackPath
        }));
        addLog(`Directory set: ${fallbackPath} (web-only mode)`);
      }
    }
  }

  async function startProcessing() {
    const currentState = get(appState);
    if (!currentState.directory) {
      addLog('❌ Error: No directory selected');
      return;
    }
    
    appState.update(state => ({
      ...state,
      isProcessing: true,
      progress: 0,
      logs: []
    }));
    
    try {
      if (currentState.tauriAvailable) {
        // Full desktop mode with Tauri backend
        addLog(`🚀 Starting desktop processing: ${currentState.directory}`);
        addLog(`⚙️ Config: Model=${currentState.config.model}, Quality=${currentState.config.quality}, Lossless=${currentState.config.lossless}`);
        
        await invoke('run_script', {
          path: currentState.directory,
          quality: currentState.config.quality,
          lossless: currentState.config.lossless,
          model: currentState.config.model
        });
        addLog('✅ Processing complete!');
        
      } else {
        // Web-only mode simulation with realistic processing steps
        addLog('🌐 Web mode: Simulating AI image processing...');
        addLog(`📁 Processing directory: ${currentState.directory}`);
        addLog(`🤖 Using model: ${currentState.config.model}`);
        addLog(`🔧 Quality settings: ${currentState.config.lossless ? 'Lossless' : `${currentState.config.quality}% quality`}`);
        
        const steps = [
          '🔍 Scanning directory for images...',
          '📊 Analyzing image characteristics...',
          '🤖 Loading AI model...',
          '🖼️ Processing images with AI descriptions...',
          '💾 Optimizing file formats...',
          '✨ Applying compression settings...',
          '📝 Generating metadata...',
          '🎯 Finalizing output...'
        ];
        
        for (let i = 0; i < steps.length; i++) {
          await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 500));
          const progress = Math.round(((i + 1) / steps.length) * 100);
          appState.update(state => ({ ...state, progress }));
          addLog(steps[i]);
        }
        
        addLog('✅ Simulation complete! In desktop mode, this would process actual images with AI.');
        addLog('💡 Tip: Install desktop dependencies to enable full functionality.');
      }
      
    } catch (error) {
      const errorMsg = error.toString();
      if (errorMsg.includes('invoke') || errorMsg.includes('tauri')) {
        addLog('⚠️ Desktop API unavailable - falling back to web simulation');
        // Fallback to simulation mode
        await startProcessing();
        return;
      } else {
        addLog(`❌ Processing error: ${error}`);
        console.error('Processing error:', error);
      }
    } finally {
      appState.update(state => ({
        ...state,
        isProcessing: false,
        progress: 100
      }));
    }
  }

  /** @param {string} message */
  function addLog(message) {
    appState.update(state => ({
      ...state,
      logs: [...state.logs, `[${new Date().toLocaleTimeString()}] ${message}`]
    }));
  }
</script>

<!-- Modern gradient header with glass morphism -->
<header class="sticky top-0 z-50 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 backdrop-blur-sm">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center py-4">
      <div class="flex items-center space-x-6">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-white">JTG AI Image Converter</h1>
        </div>
        
        <!-- Enhanced mode indicator -->
        <div class="hidden sm:flex items-center">
          <span class="text-xs font-medium text-white text-opacity-80 mr-2">MODE:</span>
          <div class="px-3 py-1 rounded-full text-xs font-medium backdrop-blur-sm border border-white border-opacity-20" 
               class:bg-green-500={$appState.mode === 'desktop' && $appState.tauriAvailable} 
               class:bg-opacity-30={$appState.mode === 'desktop' && $appState.tauriAvailable}
               class:text-green-100={$appState.mode === 'desktop' && $appState.tauriAvailable}
               class:bg-amber-500={$appState.mode === 'desktop' && !$appState.tauriAvailable} 
               class:bg-opacity-30={$appState.mode === 'desktop' && !$appState.tauriAvailable}
               class:text-amber-100={$appState.mode === 'desktop' && !$appState.tauriAvailable}
               class:bg-blue-500={$appState.mode === 'web'}
               class:bg-opacity-30={$appState.mode === 'web'}
               class:text-blue-100={$appState.mode === 'web'}
               class:bg-yellow-500={$appState.mode === 'detecting'}
               class:bg-opacity-30={$appState.mode === 'detecting'}
               class:text-yellow-100={$appState.mode === 'detecting'}
               class:animate-pulse={$appState.mode === 'detecting'}>
            {#if $appState.mode === 'detecting'}
              🔍 Detecting Environment...
            {:else if $appState.mode === 'desktop' && $appState.tauriAvailable}
              🖥️ Desktop (Full Features)
            {:else if $appState.mode === 'desktop' && !$appState.tauriAvailable}
              ⚠️ Desktop (Limited)
            {:else}
              🌐 Web Application
            {/if}
          </div>
        </div>
      </div>
      
      <!-- Settings toggle button -->
      <button 
        on:click={() => appState.update(state => ({ ...state, showSidebar: !state.showSidebar }))} 
        class="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white/50">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d={$appState.showSidebar ? "M6 18L18 6M6 6l12 12" : "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"} />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>
    </div>
  </div>
</header>

<!-- Main content area with improved layout -->
<main class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="grid grid-cols-1 {$appState.showSidebar ? 'lg:grid-cols-4' : 'lg:grid-cols-1'} gap-8">
      
      <!-- Central drop zone -->
      <div class="{$appState.showSidebar ? 'lg:col-span-3' : 'lg:col-span-1'}">
        <div class="bg-white rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden">
          <div class="p-8">
            <div 
              role="button" 
              tabindex="0" 
              class="relative group w-full min-h-[400px] border-3 border-dashed border-gray-300 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 flex flex-col items-center justify-center p-8 transition-all duration-300 hover:border-blue-400 hover:bg-gradient-to-br hover:from-blue-100 hover:to-indigo-100 focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500"
              on:drop|preventDefault={(e) => {
                addLog('📁 Directory dropped via drag & drop');
              }}
              on:dragover|preventDefault
              on:dragenter|preventDefault
              on:click={selectDirectory}
              on:keydown={(e) => { if (e.key === 'Enter') selectDirectory(); }}>
              
              <!-- Upload icon with animation -->
              <div class="relative mb-6">
                <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                  <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-5l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                </div>
                <div class="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                  <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" />
                  </svg>
                </div>
              </div>
              
              <!-- Text content -->
              <div class="text-center space-y-4">
                <h3 class="text-2xl font-bold text-gray-800">Select Image Directory</h3>
                <p class="text-gray-600 max-w-md mx-auto leading-relaxed">
                  Drag and drop a folder containing images, or click here to browse and select a directory
                </p>
                
                {#if $appState.directory}
                  <div class="mt-6 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
                    <div class="flex items-center justify-center space-x-2">
                      <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span class="text-sm font-medium text-gray-700">Selected Directory:</span>
                    </div>
                    <p class="mt-1 text-sm text-gray-900 font-mono bg-gray-50 px-3 py-2 rounded border break-all">
                      {$appState.directory}
                    </p>
                  </div>
                {/if}
                
                <div class="flex items-center justify-center space-x-4 text-xs text-gray-500 mt-6">
                  <div class="flex items-center space-x-1">
                    <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                    <span>JPG, PNG, WEBP</span>
                  </div>
                  <div class="flex items-center space-x-1">
                    <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                    <span>AI Processing</span>
                  </div>
                  <div class="flex items-center space-x-1">
                    <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
                    <span>Batch Conversion</span>
                  </div>
                </div>
              </div>
              
              <!-- Hover overlay -->
              <div class="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-indigo-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl"></div>
            </div>
          </div>
        </div>
      </div>
      <!-- Enhanced sidebar -->
      {#if $appState.showSidebar}
        <div class="lg:col-span-1">
          <div class="bg-white rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden">
            <div class="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-4">
              <h2 class="text-lg font-semibold text-white flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Configuration
              </h2>
            </div>
            
            <div class="p-6 space-y-6">
              <!-- AI Model Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  <span class="flex items-center">
                    <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    AI Model
                  </span>
                </label>
                <select bind:value={$appState.config.model} class="block w-full rounded-lg border-gray-300 bg-white shadow-sm focus:border-blue-500 focus:ring-blue-500 transition-colors duration-200">
                  <option value="llava">LLaVA (Vision + Language)</option>
                  <option value="gpt-4-vision">GPT-4 Vision (Premium)</option>
                  <option value="claude-3-vision">Claude 3 Vision</option>
                </select>
                <p class="mt-1 text-xs text-gray-500">Choose AI model for intelligent filename generation</p>
              </div>
              
              <!-- Processing Mode -->
              <div>
                <label class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
                  <input type="checkbox" bind:checked={$appState.config.lossless} class="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                  <div class="ml-3">
                    <span class="text-sm font-medium text-gray-700">Lossless Compression</span>
                    <p class="text-xs text-gray-500">Preserve original image quality (larger file sizes)</p>
                  </div>
                </label>
              </div>
              
              <!-- Quality Slider -->
              {#if !$appState.config.lossless}
                <div class="space-y-3">
                  <label class="block text-sm font-medium text-gray-700">
                    <span class="flex items-center justify-between">
                      <span class="flex items-center">
                        <svg class="w-4 h-4 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                        </svg>
                        Quality Level
                      </span>
                      <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">{$appState.config.quality}%</span>
                    </span>
                  </label>
                  <div class="relative">
                    <input 
                      type="range" 
                      min="10" 
                      max="100" 
                      step="5"
                      bind:value={$appState.config.quality} 
                      class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider" 
                    />
                    <div class="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Small</span>
                      <span>Balanced</span>
                      <span>High Quality</span>
                    </div>
                  </div>
                </div>
              {/if}
              
              <!-- Processing Features -->
              <div class="border-t border-gray-200 pt-4">
                <h3 class="text-sm font-medium text-gray-700 mb-3">Features</h3>
                <div class="space-y-2">
                  <div class="flex items-center justify-between p-2 rounded-lg bg-green-50 border border-green-200">
                    <span class="text-sm text-green-800">✨ AI Filename Generation</span>
                    <span class="text-xs text-green-600 font-medium">ENABLED</span>
                  </div>
                  <div class="flex items-center justify-between p-2 rounded-lg bg-blue-50 border border-blue-200">
                    <span class="text-sm text-blue-800">🚀 WebP Conversion</span>
                    <span class="text-xs text-blue-600 font-medium">ENABLED</span>
                  </div>
                  <div class="flex items-center justify-between p-2 rounded-lg bg-purple-50 border border-purple-200">
                    <span class="text-sm text-purple-800">⚡ Batch Processing</span>
                    <span class="text-xs text-purple-600 font-medium">ENABLED</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
</main>

  <!-- Enhanced footer with better design -->
  <div class="bg-white border-t border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="space-y-4">
        
        <!-- Action button and progress -->
        <div class="flex items-center space-x-4">
          <button 
            on:click={startProcessing} 
            disabled={!$isReady} 
            class="group relative px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed disabled:hover:translate-y-0 focus:outline-none focus:ring-4 focus:ring-green-500/50">
            <div class="flex items-center space-x-2">
              {#if $appState.isProcessing}
                <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Processing Images...</span>
              {:else}
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M12 5v.01M12 19v.01M12 23a9 9 0 100-18 9 9 0 000 18z" />
                </svg>
                <span>Start AI Processing</span>
              {/if}
            </div>
          </button>
          
          <div class="flex-1 max-w-md">
            <div class="flex items-center justify-between text-sm text-gray-600 mb-1">
              <span>Progress</span>
              <span class="font-medium">{$appState.progress}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div class="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out" 
                   style="width: {$appState.progress}%"></div>
            </div>
          </div>
        </div>
        
        <!-- Enhanced logs section -->
        <details class="group" open={$appState.logs.length > 0}>
          <summary class="flex items-center justify-between cursor-pointer p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <span class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-gray-600 group-open:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              <span class="font-medium text-gray-700">Activity Logs</span>
            </span>
            <span class="text-xs text-gray-500 bg-white px-2 py-1 rounded-full">
              {$appState.logs.length} entries
            </span>
          </summary>
          
          <div class="mt-3 bg-gray-900 rounded-lg overflow-hidden">
            <div class="bg-gray-800 px-4 py-2 border-b border-gray-700">
              <div class="flex items-center space-x-2 text-xs text-gray-300">
                <div class="flex space-x-1">
                  <div class="w-2 h-2 bg-red-500 rounded-full"></div>
                  <div class="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
                <span>JTG AI Image Converter - Activity Monitor</span>
              </div>
            </div>
            
            <div class="p-4 max-h-64 overflow-y-auto font-mono text-sm space-y-1" style="scrollbar-width: thin;">
              {#each $visibleLogs as log, i}
                <div class="flex items-start space-x-2 hover:bg-gray-800/50 px-2 py-1 rounded transition-colors">
                  <span class="text-gray-500 text-xs mt-0.5 flex-shrink-0">
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <p class="text-gray-300 leading-relaxed" 
                     class:text-red-400={log.includes('Error') || log.includes('❌')} 
                     class:text-green-400={log.includes('complete') || log.includes('✅')} 
                     class:text-blue-400={log.includes('🌐') || log.includes('🖥️')}
                     class:text-yellow-400={log.includes('⚠️') || log.includes('🔍')}
                     class:text-purple-400={log.includes('🚀') || log.includes('✨')}>
                    {log}
                  </p>
                </div>
              {/each}
              
              {#if $appState.logs.length === 0}
                <div class="text-center py-8 text-gray-500">
                  <svg class="w-8 h-8 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p class="text-sm">No activity yet. Select a directory to begin.</p>
                </div>
              {/if}
              
              {#if $appState.logs.length > 100}
                <div class="text-center py-2 text-xs text-gray-500 italic border-t border-gray-700 mt-2 pt-2">
                  Showing last 100 of {$appState.logs.length} log entries
                </div>
              {/if}
            </div>
          </div>
        </details>
      </div>
    </div>
  </div>
</main>

<style>
  /* Global styles can be moved to app.css if needed */
</style>
