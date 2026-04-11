export interface ScrapedProduct {
  id: number;
  name: string;
  category: string;
  url: string;
  heading: string;
  content: string;
  scraped_at: string;
}

export interface ProductsData {
  generated_at: string;
  count: number;
  products: ScrapedProduct[];
}
