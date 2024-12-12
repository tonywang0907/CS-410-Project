# **CS410 Project Documentation**

This project implements and evaluates information retrieval models, focusing on search performance and computational sustainability. The repository includes scripts for data preprocessing, indexing, query generation, and evaluation using the Pyserini library.

---

## **Table of Contents**
* [Usage Instructions](#usage-instructions)
  * [Build and Run Commands](#build-and-run-commands)
  * [Data Preprocessing](#data-preprocessing)
  * [Indexing the Data](#indexing-the-data)
  * [Generating Queries](#generating-queries)
  * [Running the Main Script](#running-the-main-script)
* [Implementation Details](#implementation-details)
  * [Indexing](#indexing)
  * [Search Models](#search-models)
  * [Sustainability Metrics](#sustainability-metrics)
* [File Structure](#file-structure)
* [Notes for Grading](#notes-for-grading)

---

## **Usage Instructions**

### **Build and Run Commands**
1. **Generate Queries and Index Input**
    
   Use `make all` to create queries and index input:  
   ```bash
   make all
2. **Run the Main Script**
   
   Use `make run` to execute the main workflow after queries are generated:
   ```bash
   make run
3. **Clean Temporary Files**
   
   Use `make clean` to remove generated files and reset the environment:
   ```bash
   make clean

### **Data Preprocessing**
The original datasets are not in JSON format, so a bash script is used for conversion.

- **Script Location**: `data/inaugural_speeches/convert.bash`
- **Functionality**: 
  - Extracts contents from `data/original/`.
  - Converts them to JSON format.
  - Outputs the results to `data/inaugural_speeches/converted/`.


### **Indexing the Data**

To index the preprocessed data using Pyserini, run:

```bash
python -m pyserini.index.lucene \
    -collection JsonCollection \
    -input ./data/inaugural_speeches/converted/ \
    -index ./indexes/inaugural_speeches/ \
    -generator DefaultLuceneDocumentGenerator
```
This creates an index in `./indexes/inaugural_speeches/`, which the main script will use for search and evaluation.

### **Generating Queries**
To generate queries, execute:

```bash
python generate_queries.py
```
**Note**: Query generation may take a significant amount of time. For convenience, a sample file (`data/inaugural_speeches/inaugural_speeches-queries.txt`) is provided.

### **Running the Main Script**
To evaluate the search models:
1. **Build the index (as described above).**
2. **Run the main script:**
   
   ```bash
   python main.py
   ```

## **Implementation Details**

### **Indexing**
* **Input**: Preprocessed JSON files from `data/inaugural_speeches/converted/`.

* **Output**: Lucene index stored in `./indexes/inaugural_speeches/`.

* The indexing process uses the `DefaultLuceneDocumentGenerator` to convert JSON documents into a searchable format.

### **Search Models**
The following models are implemented in `main.py`:
* **BM25**: A ranking function for information retrieval.

* **RM3 Pseudo-Relevance Feedback**: Enhances the query using top-ranked results.

* **Query Likelihood (QL)**: A statistical language model for ranking.

The script evaluates these models and computes performance metrics such as `nDCG@10` and `Precision@10`.

### **Sustainability Metrics**
The project also calculates the computational sustainability cost, including energy consumption and carbon emissions, for each search model. These metrics highlight the environmental impact of the retrieval processes.
1. **Job Sustainability Cost (JSC)**
   
   **Equation**:
   
   $$JSC_{\text{min/max}} = \frac{\sum_{i=1}^{n}(C_{\text{min/max}}(i) * E(i) * p(i)) * (1 + L)}{3600}$$

   **Where**:
   * $$C_{\text{min/max}}(i)$$: CO2 emissions per kWh for energy source i
   * E(i): Total energy consumption of the job in kJ
   * p(i): Percentage of energy source i in the mix
   * L: Efficiency loss (default 8%)

2. **Amortized Sustainability Cost (ASC)**
   
   **Equation**:
   
   $$ASC = JSC + (\frac{H_{Total} * T_{Used}}{H_{Available}})$$

   **Where**:
   * JSC: Job Sustainability Cost in gCO2e
   * $$H_{Total}$$: Total CO2 emissions from manufacturing the hardware
   * $$T_{Used}$$: Duration of the job in hours
   * $$H_{Available}$$: Total hours the hardware is expected to operate over its lifetime
     
3. **Sustainability Cost Rate (SCR)**
    
   **Equation**:
   
   $$SCR = \frac{JSC}{\Delta t_{seconds}}$$

   **Where**:
   * JSC: Job Sustainability Cost in gCO2e.
   * $$\Delta t_{seconds}$$: Duration of the job in seconds
     
   
## **File Structure**

* `data/`: Contains raw datasets and processed data used for indexing.
* `indexes/`: Stores the Lucene indexes generated during the indexing process.
* `processed_corpus/`: Holds intermediate processed data used in various tasks.
* `generate_qrels.py`: Generates QRELs (query relevance judgments) using TF-IDF and cosine similarity.
* `generate_queries.py`: Creates queries from the inaugural speeches dataset by summarizing documents using a BART model.
* `main.py`: Runs the information retrieval workflow, including document retrieval, search model evaluation, and metric calculation.
* `sustainability.py`: Calculates sustainability metrics such as Job Sustainability Cost (JSC), Amortized Sustainability Cost (ASC), and Sustainability Cost Rate (SCR).
* `Makefile`: Automates tasks like generating queries, running the main workflow, and cleaning up temporary files.
* `results_inaugural_speeches.json`: Stores search results, including document scores and rankings.
* `results.txt`: Contains evaluation metrics (e.g., `nDCG@10`) and sustainability data (e.g., CO2 emissions).

## **Notes for Grading**
* The custom dataset (`inaugural_speeches`) is used to simplify grading.
* Default configurations are sufficient for testing. No changes to `main.py` or index settings are necessary for evaluation.



