from typing import List, Optional, Any

import requests


def format_keyword_ideas(keyword_data: Optional[List[Any]]) -> List[str]:
    if not keyword_data or len(keyword_data) < 2:
        print(f"ERROR: No valid keyword ideas retrieved")
        return ["\n❌ No valid keyword ideas retrieved"]
    
    data = keyword_data[1]

    result = []
    
    # 处理常规关键词推荐
    if "allIdeas" in data and "results" in data["allIdeas"]:
        all_ideas = data["allIdeas"]["results"]
        total = data["allIdeas"].get("total", 0)
        
        print(f"SUCCESS: Get {len(all_ideas)} keyword ideas (Total: {total})")
        
        for idea in all_ideas:
            simplified_idea = {
                "keyword": idea.get('keyword', 'No keyword'),
                "country": idea.get('country', '-'),
                "difficulty": idea.get('difficultyLabel', 'Unknown'),
                "volume": idea.get('volumeLabel', 'Unknown'),
                "updatedAt": idea.get('updatedAt', '-')
            }
            result.append({
                "label": "keyword ideas",
                "value": simplified_idea
            })
    
    # 处理问题类关键词推荐
    if "questionIdeas" in data and "results" in data["questionIdeas"]:
        question_ideas = data["questionIdeas"]["results"]
        total = data["questionIdeas"].get("total", 0)
        
        print(f"SUCCESS: Get {len(question_ideas)} question ideas (Total: {total})")
        
        for idea in question_ideas:
            simplified_idea = {
                "keyword": idea.get('keyword', 'No keyword'),
                "country": idea.get('country', '-'),
                "difficulty": idea.get('difficultyLabel', 'Unknown'),
                "volume": idea.get('volumeLabel', 'Unknown'),
                "updatedAt": idea.get('updatedAt', '-')
            }
            result.append({
                "label": "question ideas",
                "value": simplified_idea
            })
    
    if not result:
        print(f"ERROR: No valid keyword ideas retrieved")
        return ["\n❌ No valid keyword ideas retrieved"]
    
    return result


def get_keyword_ideas(token: str, keyword: str, country: str = "us", search_engine: str = "Google") -> Optional[List[str]]:
    print(f"Getting keyword ideas, keyword: {keyword}, country: {country}, search engine: {search_engine}...")
    
    if not token:
        print(f"Failed to get verification token")
        return None
    
    url = "https://ahrefs.com/v4/stGetFreeKeywordIdeas"
    payload = {
        "withQuestionIdeas": True,
        "captcha": token,
        "searchEngine": search_engine,
        "country": country,
        "keyword": ["Some", keyword]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(response.text)
        return None
    
    data = response.json()

    return format_keyword_ideas(data)
