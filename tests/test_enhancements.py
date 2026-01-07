from core import NeoDict, Word, WordEntry
from crawler import WordExtractor
import os

def test_extractor_improvements():
    print("Testing Extractor Improvements...")
    extractor = WordExtractor()
    text = "最新のChatGPTやGPT-4o、それに.NETについても学びます。人工知能の発展は凄まじい。"
    
    results = extractor.extract_all(text)
    print(f"Extracted Alphanum: {results['alphanum']}")
    print(f"Extracted Kanji Compounds: {results['kanji_compounds']}")
    
    assert "ChatGPT" in results['alphanum']
    assert "GPT-4o" in results['alphanum']
    assert ".NET" in results['alphanum']
    assert "人工知能" in results['kanji_compounds']

def test_reading_estimation():
    print("\nTesting Reading Estimation...")
    nd = NeoDict()
    reading = nd.suggest_reading("生成AI")
    print(f"Suggested reading for '生成AI': {reading}")
    assert reading == "セイセイAI" or reading == "セイセイエーアイ" or "セイセイ" in reading

def test_wikipedia_reading_extraction():
    print("\nTesting Wikipedia Reading Extraction...")
    from crawler.wikipedia import WikipediaCrawler
    crawler = WikipediaCrawler()
    text = "生成AI（せいせいエーアイ、英: Generative AI）は、人工知能の一種である。"
    reading = crawler._extract_reading(text, "生成AI")
    print(f"Extracted reading from Wikipedia text: {reading}")
    assert reading == "せいせいエーアイ"

def test_multi_format_export():
    print("\nTesting Multi-Format Export...")
    nd = NeoDict(":memory:")
    nd.add_word("生成AI", reading="セイセイエーアイ")
    
    if not os.path.exists("test_exports"):
        os.makedirs("test_exports")
        
    nd.export_mecab("test_exports")
    nd.export_sudachi("test_exports")
    nd.export_janome("test_exports")
    
    print("Export files created in test_exports/")
    assert os.path.exists("test_exports/neodict.csv")
    assert os.path.exists("test_exports/neodict_sudachi.csv")
    assert os.path.exists("test_exports/neodict_janome.csv")

if __name__ == "__main__":
    test_extractor_improvements()
    test_reading_estimation()
    test_wikipedia_reading_extraction()
    test_multi_format_export()
    print("\nAll tests passed!")
