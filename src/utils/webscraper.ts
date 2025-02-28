import axios from 'axios';
import * as cheerio from 'cheerio';

interface ScrapedContent {
  title: string;
  description: string;
  mainContent: string;
  relevantSections: string[];
  aiRelatedContent: string[];
}

export async function scrapeWebsite(url: string): Promise<ScrapedContent> {
  try {
    // Ensure URL has protocol
    if (!url.startsWith('http')) {
      url = `https://${url}`;
    }

    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; AIRegulationAnalyzer/1.0; +http://example.com)'
      }
    });

    const $ = cheerio.load(response.data);

    // Initialize content object
    const content: ScrapedContent = {
      title: '',
      description: '',
      mainContent: '',
      relevantSections: [],
      aiRelatedContent: []
    };

    // Get page title
    content.title = $('title').text().trim();

    // Get meta description
    content.description = $('meta[name="description"]').attr('content') || '';

    // Get main content (focusing on common content containers)
    const mainContentSelectors = ['main', 'article', '#content', '.content', '#main', '.main'];
    for (const selector of mainContentSelectors) {
      const mainContent = $(selector).text().trim();
      if (mainContent) {
        content.mainContent = mainContent;
        break;
      }
    }

    // Find AI-related content
    const aiKeywords = ['AI', 'artificial intelligence', 'machine learning', 'ML', 'deep learning',
                       'neural network', 'automation', 'data science', 'algorithm'];
    
    $('p, h1, h2, h3, h4, h5, h6').each((_, element) => {
      const text = $(element).text().trim();
      if (text.length > 0) {
        // Check if the text contains AI-related keywords
        const containsAIKeyword = aiKeywords.some(keyword => 
          text.toLowerCase().includes(keyword.toLowerCase())
        );
        
        if (containsAIKeyword) {
          content.aiRelatedContent.push(text);
        }
      }
    });

    // Find sections that might be about the company
    const companySelectors = ['#about', '.about', 'about-us', '.company', '#company'];
    companySelectors.forEach(selector => {
      const section = $(selector).text().trim();
      if (section) {
        content.relevantSections.push(section);
      }
    });

    return content;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to scrape website: ${error.message}`);
    }
    throw error;
  }
}

export async function validateWebsite(url: string): Promise<boolean> {
  try {
    const formattedUrl = url.startsWith('http') ? url : `https://${url}`;
    await axios.head(formattedUrl);
    return true;
  } catch (error) {
    return false;
  }
}