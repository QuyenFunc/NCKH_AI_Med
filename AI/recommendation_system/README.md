# 🏥 Health Content Recommendation System

An intelligent, personalized health content recommendation system that analyzes user profiles and provides curated health articles using OpenRouter AI.

## 🎯 Overview

This system replaces the old ML-based news system with a more practical approach:

- **AI-Powered Analysis**: Uses OpenRouter API to analyze user health profiles
- **Background Processing**: Analyzes profiles asynchronously to avoid blocking user experience
- **Smart Triggering**: Only runs analysis when user profile changes significantly
- **Curated Content**: Focuses on educational health content, not news
- **Personalized Matching**: Matches articles based on user's health profile and needs

## 🏗️ Architecture

```
User Profile Update → Background Analysis → Content Matching → Personalized Feed
                           ↓
                    OpenRouter AI Analysis
                           ↓
                    Category + Keywords + Reasoning
                           ↓
                    Article Database Matching
                           ↓
                    Personalized Article List
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd AI/recommendation_system
pip install -r requirements.txt
```

### 2. Set OpenRouter API Key (Optional)

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

*Note: System includes a default key for testing*

### 3. Start the Service

```bash
python start_recommendation_service.py
```

### 4. Test the System

```bash
python test_system.py
```

## 📡 API Endpoints

### Base URL: `http://localhost:5002`

#### 1. Health Check
```http
GET /health
```

#### 2. Analyze User Profile
```http
POST /recommendations/analyze-profile
Content-Type: application/json

{
    "user_id": "user123",
    "profile": {
        "age": 35,
        "gender": "female",
        "height": 165,
        "weight": 70,
        "medical_history": ["hypertension"],
        "allergies": ["penicillin"],
        "lifestyle": {
            "exercise": "moderate",
            "smoking": "no",
            "alcohol": "occasional"
        },
        "health_goals": ["lose weight", "manage blood pressure"]
    }
}
```

#### 3. Get User Recommendations
```http
GET /recommendations/user/{user_id}?limit=20&category=Heart%20Health
```

#### 4. Get Trending Articles
```http
GET /recommendations/trending?limit=10&category=Nutrition
```

#### 5. Track Article Clicks
```http
POST /recommendations/track-click
Content-Type: application/json

{
    "user_id": "user123",
    "article_id": "heart_001"
}
```

## 🧠 How It Works

### 1. Profile Analysis
When a user updates their profile:
1. System checks if profile changed significantly
2. If yes, queues background analysis job
3. OpenRouter AI analyzes profile and generates recommendations
4. Results stored in database for fast retrieval

### 2. Content Matching
- Matches AI recommendations with curated health articles
- Uses category matching, keyword overlap, and credibility scoring
- Prioritizes based on user's health conditions and goals

### 3. Background Processing
- All AI analysis happens in background
- Users don't wait for processing
- Results cached for immediate access

## 📊 Content Categories

- **Heart Health & Cardiovascular**
- **Nutrition & Diet**
- **Exercise & Fitness**
- **Mental Health & Stress Management**
- **Preventive Care & Screening**
- **Sleep & Recovery**
- **Women's Health** / **Men's Health**
- **Chronic Disease Management**
- **Weight Management**
- **Bone & Joint Health**
- **Immune System Support**

## 🗄️ Database Schema

### User Recommendations
```sql
user_recommendations (
    user_id, category, priority, topics, 
    reasoning, keywords, created_at
)
```

### Health Articles
```sql
health_articles (
    id, title, summary, category, keywords,
    target_audience, medical_conditions,
    credibility_score, source, url
)
```

### Content Matches
```sql
user_content_matches (
    user_id, article_id, match_score,
    shown_at, clicked
)
```

## 🔧 Integration with Spring Boot

### Backend Service Call
```java
@Service
public class RecommendationService {
    
    @Value("${recommendation.service.url:http://localhost:5002}")
    private String recommendationServiceUrl;
    
    public void analyzeUserProfile(String userId, UserProfile profile) {
        // Call recommendation service asynchronously
        CompletableFuture.runAsync(() -> {
            try {
                Map<String, Object> payload = Map.of(
                    "user_id", userId,
                    "profile", convertToProfileData(profile)
                );
                
                restTemplate.postForEntity(
                    recommendationServiceUrl + "/recommendations/analyze-profile",
                    payload,
                    String.class
                );
            } catch (Exception e) {
                log.error("Failed to analyze profile for user: {}", userId, e);
            }
        });
    }
    
    public List<ArticleDto> getUserRecommendations(String userId, int limit) {
        try {
            String url = recommendationServiceUrl + 
                "/recommendations/user/" + userId + "?limit=" + limit;
            
            ResponseEntity<RecommendationResponse> response = 
                restTemplate.getForEntity(url, RecommendationResponse.class);
            
            return response.getBody().getArticles();
        } catch (Exception e) {
            log.error("Failed to get recommendations for user: {}", userId, e);
            return Collections.emptyList();
        }
    }
}
```

### Trigger Points
1. **User Registration**: Analyze initial profile
2. **Profile Update**: Re-analyze if significant changes
3. **Settings Save**: Check for health goal changes

## 🔍 Monitoring & Analytics

### System Stats Endpoint
```http
GET /recommendations/stats
```

Returns:
- Total articles in database
- Users with recommendations
- Content match statistics
- Click-through rates

### Logging
- All operations logged with timestamps
- Background job status tracking
- API request/response logging
- Error tracking and reporting

## 🛠️ Development

### Adding New Content Categories
1. Update `content_matcher.py` categories list
2. Add sample articles in `populate_sample_articles()`
3. Update OpenRouter prompts in `openrouter_client.py`

### Customizing AI Analysis
Edit prompts in `openrouter_client.py`:
```python
def _create_analysis_prompt(self, profile: UserProfile) -> str:
    # Customize prompt based on your needs
```

### Testing
```bash
# Run comprehensive tests
python test_system.py

# Test individual components
python -c "from openrouter_client import test_openrouter_client; import asyncio; asyncio.run(test_openrouter_client())"
```

## 🚨 Error Handling

- **OpenRouter API Failures**: Falls back to predefined recommendations
- **Database Errors**: Graceful degradation with logging
- **Background Job Failures**: Retry mechanism with exponential backoff
- **Network Issues**: Timeout handling and circuit breaker pattern

## 📈 Performance

- **Background Processing**: No blocking operations for users
- **Caching**: Recommendations cached until profile changes
- **Database Optimization**: Indexed queries for fast retrieval
- **Memory Efficient**: Streaming responses for large datasets

## 🔐 Security

- **API Key Management**: Environment variable configuration
- **Input Validation**: All endpoints validate input data
- **SQL Injection Protection**: Parameterized queries
- **Rate Limiting**: Built-in Flask rate limiting

## 🚀 Deployment

### Production Setup
1. Set production OpenRouter API key
2. Configure proper logging levels
3. Set up database backups
4. Monitor system resources
5. Configure reverse proxy (nginx)

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5002
CMD ["python", "start_recommendation_service.py"]
```

## 📞 Support

For issues or questions:
1. Check logs in the console output
2. Verify OpenRouter API key configuration
3. Test individual components using test scripts
4. Check database file permissions

---

Built with ❤️ for personalized health content recommendation
