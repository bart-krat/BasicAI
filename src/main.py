import asyncio
import os
from dotenv import load_dotenv
import PyPDF2  
from agent import Agent
from parser import StructuredOutputParser
import matplotlib.pyplot as plt
import json


# Load environment variables
input_dir = "/Users/bartkratochvil/Desktop/BasicAI/data/Climate"

def process_files(input_dir: str):
    """Process all files in the input directory (txt and pdf)"""
    all_text = []  # Store all file contents
    
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        
        if file.endswith(".txt"):
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    text = f.read()
                    all_text.append({"filename": file, "content": text, "type": "txt"})
                    print(f"✅ Processed TXT: {file} ({len(text)} characters)")
            except Exception as e:
                print(f"❌ Error reading TXT {file}: {e}")
                
        elif file.endswith(".pdf"):
            try:
                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text()
                    
                    all_text.append({"filename": file, "content": text, "type": "pdf"})
                    print(f"✅ Processed PDF: {file} ({len(text)} characters, {len(pdf_reader.pages)} pages)")
            except Exception as e:
                print(f"❌ Error reading PDF {file}: {e}")
    
    return all_text


load_dotenv()

async def extract_data(files_data):
    """Extract climate data from all files using LLM"""
    
    system_prompt = """You are a data extractor. You are given a text and you need to extract the climate data from the text.

    The data you need to extract is:
    - Mean annual temperature
    - Mean annual rainfall
    - Mean annual sunlight

    There is other data that exists in the text that refers to monthly data, ignore this and only extract the annual mean which is provided towards the end of the text.
    Make sure you output this in a JSON format.
    
    Example:
    ```json
    {
        "year": 2020, 
        "mean_annual_temperature": 20,
        "mean_annual_rainfall": 100,
        "mean_annual_sunlight": 1000
    }```"""
    
    # Create agent
    data_agent = Agent(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Create JSON parser
    parser = StructuredOutputParser()
    
    extracted_data = []
    
    print(f"🔍 Extracting data from {len(files_data)} files...")
    
    for file_info in files_data:
        filename = file_info["filename"]
        content = file_info["content"]
        
        print(f"📄 Processing: {filename}")
        
        try:
            # Generate response from LLM
            user_prompt = f"Here is the text: {content}"
            response = await data_agent.generate(
                prompt=user_prompt,
                system_message=system_prompt
            )
            
            # Parse JSON response
            parse_result = parser.parse_json(response)
            
            if parse_result.success:
                # Add filename to the extracted data
                extracted_data.append({
                    "filename": filename,
                    "extracted_data": parse_result.data
                })
                print(f"✅ Successfully extracted data from {filename}")
            else:
                print(f"❌ Failed to parse JSON from {filename}: {parse_result.error}")
                # Try to extract JSON from the response
                auto_parse_result = parser.auto_parse(response, preferred_format="json")
                if auto_parse_result.success:
                    extracted_data.append({
                        "filename": filename,
                        "extracted_data": auto_parse_result.data
                    })
                    print(f"✅ Successfully extracted data from {filename} (auto-parse)")
                else:
                    print(f"❌ Could not extract data from {filename}")
                    
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    
    print(f"📊 Successfully extracted data from {len(extracted_data)} files")
    return extracted_data


def create_climate_graphs(extracted_data):
    """Create line graphs for climate data"""
    if not extracted_data:
        print("❌ No data to visualize")
        return
    
    # Prepare data for plotting
    data_points = []
    
    for item in extracted_data:
        data = item['extracted_data']
        if isinstance(data, dict) and data.get('year'):
            data_points.append({
                'year': data.get('year', 0),
                'temperature': data.get('mean_annual_temperature', 0),
                'rainfall': data.get('mean_annual_rainfall', 0),
                'sunlight': data.get('mean_annual_sunlight', 0)
            })
    
    if not data_points:
        print("❌ No valid data found for visualization")
        return
    
    # Sort data by year to ensure proper chronological order
    data_points.sort(key=lambda x: x['year'])
    
    # Extract sorted data
    years = [point['year'] for point in data_points]
    temperatures = [point['temperature'] for point in data_points]
    rainfalls = [point['rainfall'] for point in data_points]
    sunlights = [point['sunlight'] for point in data_points]
    
    # Create figure with 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
    
    # Temperature graph
    ax1.plot(years, temperatures, 'b-o', linewidth=2, markersize=6)
    ax1.set_title('Mean Annual Temperature Over Time', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Temperature (°C)')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(years)
    
    # Rainfall graph
    ax2.plot(years, rainfalls, 'g-o', linewidth=2, markersize=6)
    ax2.set_title('Mean Annual Rainfall Over Time', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Rainfall (mm)')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(years)
    
    # Sunlight graph
    ax3.plot(years, sunlights, 'orange', marker='o', linewidth=2, markersize=6)
    ax3.set_title('Mean Annual Sunlight Over Time', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Sunlight (hours)')
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks(years)
    
    # Adjust layout and show
    plt.tight_layout()
    plt.show()
    
    print(f"📈 Created climate graphs for {len(years)} data points")


async def main():
    input_dir = "/Users/bartkratochvil/Desktop/BasicAI/data/Climate"
    
    # Step 1: Process files
    print("📁 Processing files...")
    files_data = process_files(input_dir)
    
    # Step 2: Extract data
    print("\n🔍 Extracting climate data...")
    extracted_data = await extract_data(files_data)
    
    # Step 3: Show results
    print(f"\n📊 Final results:")
    for item in extracted_data:
        print(f"File: {item['filename']}")
        print(f"Data: {item['extracted_data']}")
    
    # Step 4: Create visualizations
    print(f"\n📈 Creating climate graphs...")
    create_climate_graphs(extracted_data)

if __name__ == "__main__":
    asyncio.run(main())
