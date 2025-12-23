use flutter_rust_bridge::frb;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Tokenization result structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Token {
    pub text: String,
    pub position: usize,
    pub token_type: TokenType,
}

/// Type of token
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TokenType {
    Word,
    Number,
    Punctuation,
    Whitespace,
}

/// NLP processing result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NlpResult {
    pub tokens: Vec<Token>,
    pub word_count: usize,
    pub sentence_count: usize,
    pub entities: Vec<Entity>,
    pub sentiment: Sentiment,
    pub intent: Option<String>,
}

/// Named entity
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Entity {
    pub text: String,
    pub entity_type: EntityType,
    pub confidence: f32,
}

/// Entity type classification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EntityType {
    Person,
    Location,
    Organization,
    Date,
    Time,
    Number,
    Other,
}

/// Sentiment analysis result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Sentiment {
    Positive,
    Negative,
    Neutral,
}

/// Core NLP processing module
pub struct NlpProcessor {
    word_regex: Regex,
    number_regex: Regex,
    sentence_regex: Regex,
    entity_patterns: HashMap<EntityType, Regex>,
}

impl NlpProcessor {
    /// Create a new NLP processor
    pub fn new() -> Self {
        Self {
            word_regex: Regex::new(r"\b\w+\b").unwrap(),
            number_regex: Regex::new(r"\b\d+\.?\d*\b").unwrap(),
            sentence_regex: Regex::new(r"[.!?]+").unwrap(),
            entity_patterns: create_entity_patterns(),
        }
    }

    /// Process text and extract NLP features
    #[frb(sync)]
    pub fn process_text(&self, text: String) -> NlpResult {
        let tokens = self.tokenize(&text);
        let word_count = self.count_words(&tokens);
        let sentence_count = self.count_sentences(&text);
        let entities = self.extract_entities(&text);
        let sentiment = self.analyze_sentiment(&text);
        let intent = self.detect_intent(&text);

        NlpResult {
            tokens,
            word_count,
            sentence_count,
            entities,
            sentiment,
            intent,
        }
    }

    /// Tokenize text into words, numbers, and punctuation
    fn tokenize(&self, text: &str) -> Vec<Token> {
        let mut tokens = Vec::new();
        let mut pos = 0;

        for mat in self.word_regex.find_iter(text) {
            // Add any whitespace before this match
            if pos < mat.start() {
                let whitespace = &text[pos..mat.start()];
                tokens.push(Token {
                    text: whitespace.to_string(),
                    position: pos,
                    token_type: TokenType::Whitespace,
                });
            }

            // Add the word token
            tokens.push(Token {
                text: mat.as_str().to_string(),
                position: mat.start(),
                token_type: TokenType::Word,
            });

            pos = mat.end();
        }

        // Handle any remaining text
        if pos < text.len() {
            let remaining = &text[pos..];
            tokens.push(Token {
                text: remaining.to_string(),
                position: pos,
                token_type: TokenType::Punctuation,
            });
        }

        tokens
    }

    /// Count the number of words in tokens
    fn count_words(&self, tokens: &[Token]) -> usize {
        tokens.iter()
            .filter(|token| matches!(token.token_type, TokenType::Word))
            .count()
    }

    /// Count the number of sentences
    fn count_sentences(&self, text: &str) -> usize {
        self.sentence_regex.find_iter(text).count()
    }

    /// Extract named entities from text
    fn extract_entities(&self, text: &str) -> Vec<Entity> {
        let mut entities = Vec::new();

        for (entity_type, pattern) in &self.entity_patterns {
            for mat in pattern.find_iter(text) {
                entities.push(Entity {
                    text: mat.as_str().to_string(),
                    entity_type: entity_type.clone(),
                    confidence: 0.9, // Default confidence
                });
            }
        }

        entities
    }

    /// Analyze sentiment of text
    fn analyze_sentiment(&self, text: &str) -> Sentiment {
        let lower_text = text.to_lowercase();
        
        // Simple keyword-based sentiment analysis
        let positive_keywords = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like", "happy", "joy"];
        let negative_keywords = ["bad", "terrible", "awful", "horrible", "hate", "dislike", "sad", "angry", "disappointed", "frustrated"];
        
        let positive_count = positive_keywords.iter().filter(|&word| lower_text.contains(word)).count();
        let negative_count = negative_keywords.iter().filter(|&word| lower_text.contains(word)).count();
        
        if positive_count > negative_count {
            Sentiment::Positive
        } else if negative_count > positive_count {
            Sentiment::Negative
        } else {
            Sentiment::Neutral
        }
    }

    /// Detect intent from text
    fn detect_intent(&self, text: &str) -> Option<String> {
        let lower_text = text.to_lowercase();
        
        if lower_text.contains("hello") || lower_text.contains("hi") || lower_text.contains("hey") {
            Some("greeting".to_string())
        } else if lower_text.contains("help") || lower_text.contains("assist") {
            Some("request_help".to_string())
        } else if lower_text.contains("thank") {
            Some("gratitude".to_string())
        } else if lower_text.contains("bye") || lower_text.contains("goodbye") {
            Some("farewell".to_string())
        } else {
            None
        }
    }
}

/// Create regex patterns for entity extraction
fn create_entity_patterns() -> HashMap<EntityType, Regex> {
    let mut patterns = HashMap::new();
    
    // Person names (simple pattern)
    patterns.insert(
        EntityType::Person,
        Regex::new(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b").unwrap(),
    );
    
    // Locations (simple pattern)
    patterns.insert(
        EntityType::Location,
        Regex::new(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b").unwrap(),
    );
    
    // Organizations (simple pattern)
    patterns.insert(
        EntityType::Organization,
        Regex::new(r"\b[A-Z][A-Za-z\s]+(?:Inc|LLC|Ltd|Corp|Company|University|Institute)\b").unwrap(),
    );
    
    // Dates (simple pattern)
    patterns.insert(
        EntityType::Date,
        Regex::new(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b").unwrap(),
    );
    
    // Times (simple pattern)
    patterns.insert(
        EntityType::Time,
        Regex::new(r"\b\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?\b").unwrap(),
    );
    
    // Numbers (already handled by number_regex)
    patterns.insert(
        EntityType::Number,
        Regex::new(r"\b\d+\.?\d*\b").unwrap(),
    );
    
    patterns
}

/// Create a new NLP processor instance
#[frb(sync)]
pub fn create_nlp_processor() -> NlpProcessor {
    NlpProcessor::new()
}

/// Process text with default processor
#[frb(sync)]
pub fn process_text_simple(text: String) -> String {
    let processor = NlpProcessor::new();
    let result = processor.process_text(text);
    
    format!(
        "Processed text with {} tokens, {} words, {} sentences, {} entities. Sentiment: {:?}",
        result.tokens.len(),
        result.word_count,
        result.sentence_count,
        result.entities.len(),
        result.sentiment
    )
}