from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter

)
text = """"
The detective entered the abandaned house just before midnight. The rooms were silent, and the windows were covered with dust. On the table,he found a blood.

The man who did the crime was john. No body in the village trusted him, but he had disappeared there days before the murder. The detective immediately realized.

The next morning, the detective returned to the detective returned to the house. Behind a loose brick, he discovered a photograph a john standing beside the victim.This finally connected.
"""


#============================
# 1. FIXED SIZE CHUNKING
#============================

fixed = CharacterTextSplitter(
    separator = "",
    chunk_size=100,
    chunk_overlap=0,
)
print("\========== FIXED SIZE ==========")

for i, chunk in enumerate (fixed.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("------------")

#=============================
# 2. PARAGRAPH CHUNKING
#=============================

paragraph = CharacterTextSplitter(
    separator = "\n\n",
    chunk_size=100,
    chunk_overlap=0
)
print("\n========= PARAGRAPH ============")
for i, chunk in enumerate(paragraph.split_text(text), 1):
    print(f"\nChunk{i}:")
    print (chunk)
    print("--------------")

#============================    
# 3. RECURSIVE CHUNKING
#============================

recursive = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20
)
print("\n============= RECURSIVE =============")

for i, chunk in enumerate(recursive.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("----------------")