# Google AI Studio Integration Guide

## 🤖 How to Integrate with Google AI Studio (Gemini)

This guide shows you how to integrate the Company Data Collection system with Google AI Studio using the Gemini API.

## 🚀 Quick Start

### 1. Get Your Google AI API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the left sidebar
4. Create a new API key
5. Copy the API key (starts with `AIza...`)

### 2. Configure Your Environment

```bash
# Option 1: Update .env file
cp config.env.example .env
nano .env

# Add your API key:
GOOGLE_AI_API_KEY=AIzaSyC...your_actual_api_key_here
GOOGLE_AI_MODEL=gemini-1.5-flash

# Option 2: Set environment variable
export GOOGLE_AI_API_KEY=AIzaSyC...your_actual_api_key_here
```

### 3. Test the Integration

```bash
# Test Google AI connection
python main.py --test-google-ai

# Run with Google AI
python main.py --company "Alphabet Inc." --google-ai

# Run demo script
python google_ai_demo.py
```

## 🔧 Available Commands

### Basic Usage

```bash
# Use Google AI instead of OpenAI
python main.py --google-ai

# Test Google AI connection
python main.py --test-google-ai

# Process specific company with Google AI
python main.py --company "Microsoft Corporation" --google-ai

# Process multiple companies with Google AI
python main.py --companies "Alphabet Inc." "Microsoft Corporation" --google-ai
```

### Advanced Usage

```bash
# Verbose logging with Google AI
python main.py --company "Alphabet Inc." --google-ai --verbose

# Initialize database and use Google AI
python main.py --init-db --google-ai
```

## 🎯 What Google AI Adds

### Enhanced Features

1. **AI-Powered Data Analysis**
   - Data quality assessment (1-100 score)
   - Missing information analysis
   - Business intelligence insights
   - Recommendations for data enhancement

2. **Intelligent Report Generation**
   - Executive summary
   - Company overview
   - Digital asset analysis
   - Risk assessment
   - Competitive positioning

3. **Advanced Validation**
   - AI-enhanced validation scoring
   - Intelligent error detection
   - Contextual recommendations

### Example Output

```json
{
  "success": true,
  "company_name": "Alphabet Inc.",
  "ai_analysis": {
    "data_quality_score": 87,
    "missing_information": [
      "Recent acquisition dates",
      "Financial performance metrics"
    ],
    "business_insights": [
      "Strong digital presence with 9+ domains",
      "Diverse brand portfolio including Google, YouTube",
      "Complex corporate structure with multiple subsidiaries"
    ],
    "recommendations": [
      "Verify domain ownership through WHOIS",
      "Cross-reference with SEC filings",
      "Update acquisition timeline"
    ],
    "summary": "High-quality data with strong digital footprint"
  },
  "final_report": {
    "success": true,
    "report": "Executive Summary: Alphabet Inc. demonstrates...",
    "ai_model": "gemini-1.5-flash"
  }
}
```

## 🔄 Comparison: OpenAI vs Google AI

| Feature | OpenAI (GPT-4) | Google AI (Gemini) |
|---------|----------------|-------------------|
| **Cost** | Higher | Lower |
| **Speed** | Fast | Very Fast |
| **Context Length** | 128k tokens | 1M+ tokens |
| **Multimodal** | Yes | Yes |
| **Code Generation** | Excellent | Excellent |
| **Business Analysis** | Good | Excellent |
| **Free Tier** | Limited | Generous |

## 🛠️ Configuration Options

### Environment Variables

```bash
# Required
GOOGLE_AI_API_KEY=your_api_key_here

# Optional
GOOGLE_AI_MODEL=gemini-1.5-flash  # or gemini-1.5-pro, gemini-1.0-pro
```

### Available Models

- `gemini-1.5-flash` - Fast, cost-effective (default)
- `gemini-1.5-pro` - Most capable, higher cost
- `gemini-1.0-pro` - Stable, good performance

## 🔍 Troubleshooting

### Common Issues

1. **API Key Not Working**
   ```bash
   # Check if key is set
   echo $GOOGLE_AI_API_KEY
   
   # Test connection
   python main.py --test-google-ai
   ```

2. **Rate Limiting**
   - Google AI has generous rate limits
   - If you hit limits, wait a few minutes
   - Consider using `gemini-1.5-flash` for faster processing

3. **Model Not Available**
   - Ensure you're using a supported model name
   - Check Google AI Studio for available models

### Debug Mode

```bash
# Enable verbose logging
python main.py --google-ai --verbose

# Check logs
tail -f logs/app.log
```

## 📊 Performance Comparison

### Speed Test Results

```bash
# Test with OpenAI
time python main.py --company "Alphabet Inc."

# Test with Google AI
time python main.py --company "Alphabet Inc." --google-ai
```

**Typical Results:**
- OpenAI GPT-4: ~30-45 seconds
- Google AI Gemini: ~15-25 seconds

## 🎨 Customization

### Custom AI Prompts

You can modify the AI prompts in `src/agents/google_ai_agent.py`:

```python
# Customize the analysis prompt
prompt = f"""
Your custom prompt here...
Company Data: {json.dumps(data_summary, indent=2)}
Your custom instructions...
"""
```

### Custom Models

```python
# Use different Gemini model
self.model = genai.GenerativeModel("gemini-1.5-pro")
```

## 🔐 Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables for production**
3. **Rotate API keys regularly**
4. **Monitor usage in Google AI Studio dashboard**

## 📈 Monitoring Usage

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click on "Usage" in the left sidebar
3. Monitor your API calls and costs
4. Set up billing alerts if needed

## 🆘 Support

- **Google AI Documentation**: https://ai.google.dev/docs
- **Google AI Studio**: https://aistudio.google.com/
- **Community Support**: Google AI Developer Community

## 🎉 Next Steps

1. **Try the demo**: `python google_ai_demo.py`
2. **Process your first company**: `python main.py --google-ai`
3. **Customize the prompts** for your specific use case
4. **Monitor usage** in Google AI Studio dashboard
5. **Scale up** to process multiple companies

Happy coding with Google AI! 🚀
