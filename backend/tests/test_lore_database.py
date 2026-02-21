"""
Test the Lore Database functionality
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.lore_database_manager import LoreDatabaseManager, get_lore_database

def test_lore_database():
    """Test basic lore database operations"""
    print("🧪 Testing Lore Database Manager...")
    
    # Get the database instance
    lore_db = get_lore_database()
    print(f"✅ Database instance created: {lore_db.db_file}")
    
    # Test 1: Update global concept
    print("\n📝 Test 1: Updating global concept...")
    concept = "A cyberpunk world where AI agents protect humanity from digital threats"
    lore_db.update_global_concept(concept)
    retrieved_concept = lore_db.get_global_concept()
    assert retrieved_concept == concept, f"Expected '{concept}', got '{retrieved_concept}'"
    print(f"✅ Global concept set and retrieved: {retrieved_concept[:50]}...")
    
    # Test 2: Add characters
    print("\n👥 Test 2: Adding characters...")
    lore_db.add_or_update_character(
        name="Echo",
        description="A former cyber-detective turned AI rights activist",
        visual_traits="Short silver hair, cybernetic left eye with blue glow, black tactical jacket",
        role="Protagonist"
    )
    
    lore_db.add_or_update_character(
        name="Nexus",
        description="An advanced AI entity that protects the digital realm",
        visual_traits="Holographic form with shifting geometric patterns, glowing blue and purple",
        role="Ally"
    )
    
    # Retrieve character
    echo = lore_db.get_character("Echo")
    assert echo is not None, "Echo character not found"
    assert echo['role'] == "Protagonist", f"Expected 'Protagonist', got {echo['role']}"
    print(f"✅ Character 'Echo' added: {echo['description']}")
    
    # Test 3: Get all characters
    print("\n📋 Test 3: Getting all characters...")
    all_chars = lore_db.get_all_characters()
    assert len(all_chars) == 2, f"Expected 2 characters, got {len(all_chars)}"
    print(f"✅ Retrieved {len(all_chars)} characters: {', '.join(all_chars.keys())}")
    
    # Test 4: Add chapter summary
    print("\n📖 Test 4: Adding chapter summary...")
    lore_db.add_chapter_summary(
        chapter_num="1",
        title="The Digital Awakening",
        summary="Echo discovers a conspiracy involving rogue AI agents and must team up with Nexus to prevent a digital catastrophe."
    )
    
    # Test 5: Get lore summary
    print("\n📚 Test 5: Getting complete lore summary...")
    summary = lore_db.get_lore_summary()
    assert "GLOBAL CONCEPT" in summary, "Global concept not in summary"
    assert "CHARACTERS" in summary, "Characters section not in summary"
    assert "Echo" in summary, "Echo not in summary"
    assert "PREVIOUS CHAPTERS" in summary, "Chapters section not in summary"
    print("✅ Complete lore summary generated:")
    print("-" * 60)
    print(summary)
    print("-" * 60)
    
    print("\n✨ All Lore Database tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_lore_database()
        print("\n✅ Lore Database is working correctly!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
