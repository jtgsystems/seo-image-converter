import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Set viewport size
  await page.setViewportSize({ width: 1920, height: 1080 });
  
  try {
    console.log('📸 Taking screenshot of UI...');
    await page.goto('http://localhost:5174/', { waitUntil: 'networkidle' });
    
    // Wait a bit for the page to fully render
    await page.waitForTimeout(2000);
    
    // Take screenshot
    await page.screenshot({ path: 'ui-current.png', fullPage: true });
    console.log('✅ Screenshot saved as ui-current.png');
    
    // Get page title and basic info
    const title = await page.title();
    const url = page.url();
    console.log(`📄 Page Title: ${title}`);
    console.log(`🔗 URL: ${url}`);
    
    // Check if main elements are present
    const hasHeader = await page.locator('header').count() > 0;
    const hasMainContent = await page.locator('main').count() > 0;
    const hasFooter = await page.locator('footer').count() > 0;
    
    console.log(`🏷️  Header present: ${hasHeader}`);
    console.log(`📋 Main content present: ${hasMainContent}`);
    console.log(`🦶 Footer present: ${hasFooter}`);
    
  } catch (error) {
    console.error('❌ Error taking screenshot:', error.message);
  }
  
  await browser.close();
})();