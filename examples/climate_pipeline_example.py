"""
Climate Data Pipeline Example

This demonstrates how to use the Pipeline class for the climate data workflow
with proper state management and step-by-step execution.
"""

import asyncio
import os
from dotenv import load_dotenv
from pipeline import Pipeline
from state import StateManager
from agent import Agent
from parser import StructuredOutputParser
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Define the pipeline functions
def process_files_step(input_directory: str):
    """Step 1: Process all files in the input directory"""
    import os
    import PyPDF2
    
    all_text = []
    
    for file in os.listdir(input_directory):
        file_path = os.path.join(input_directory, file)
        
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
    
    return {"files_data": all_text, "total_files": len(all_text)}


async def extract_data_step(files_data):
    """Step 2: Extract climate data using LLM"""
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
                extracted_data.append({
                    "filename": filename,
                    "extracted_data": parse_result.data
                })
                print(f"✅ Successfully extracted data from {filename}")
            else:
                print(f"❌ Failed to parse JSON from {filename}: {parse_result.error}")
                # Try auto-parse
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
    
    return {"extracted_data": extracted_data, "successful_extractions": len(extracted_data)}


def create_visualizations_step(extracted_data):
    """Step 3: Create climate graphs"""
    if not extracted_data:
        print("❌ No data to visualize")
        return {"graphs_created": 0}
    
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
        return {"graphs_created": 0}
    
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
    return {"graphs_created": 1, "data_points": len(years)}


async def main():
    """Run the climate data pipeline using the Pipeline class"""
    
    # 1. Create state manager (this is what you need to do manually)
    state_manager = StateManager(
        session_id="climate_analysis",
        auto_save=True,
    )
    
    # 2. Initialize the pipeline with state management
    pipeline = Pipeline(
        name="Climate Data Analysis",
        state_manager=state_manager
    )
    
    # 3. Define the state schema upfront
    state_manager.define({
        "input_directory": "/Users/bartkratochvil/Desktop/BasicAI/data/Climate",
        "files_data": [],
        "extracted_data": [],
        "visualization_data": {},
        "pipeline_status": "initialized",
        "current_step": "none"
    })
    
    # 4. Add pipeline steps
    pipeline.add_step(
        step_number=1,
        name="Process Files",
        description="Read and process all TXT and PDF files from the input directory",
        input_keys=["input_directory"],
        output_keys=["files_data", "total_files"],
        function=process_files_step
    )
    
    pipeline.add_step(
        step_number=2,
        name="Extract Data",
        description="Use LLM to extract climate data from processed files",
        input_keys=["files_data"],
        output_keys=["extracted_data", "successful_extractions"],
        function=extract_data_step
    )
    
    pipeline.add_step(
        step_number=3,
        name="Create Visualizations",
        description="Generate line graphs for climate trends over time",
        input_keys=["extracted_data"],
        output_keys=["graphs_created", "data_points"],
        function=create_visualizations_step
    )
    
    # 5. Execute the pipeline
    print("🚀 Starting Climate Data Pipeline...")
    print(f"📋 Pipeline: {pipeline.name}")
    print(f"📊 Steps: {len(pipeline.steps)}")
    
    try:
        # Execute all steps
        results = await pipeline.execute_all()
        
        print("\n✅ Pipeline completed successfully!")
        print(f"📈 Results: {results}")
        
        # Show final state
        print("\n📊 Final State:")
        all_state = await state_manager.get_all()
        for key, value in all_state.items():
            if key != "files_data":  # Skip large data for display
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        print(f"📊 Current state: {await state_manager.get_all()}")


if __name__ == "__main__":
    asyncio.run(main())
