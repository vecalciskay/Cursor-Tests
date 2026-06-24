# Step 01 - Reading the Excel file and output to JSON results

Create a development plan to develop a python script that will read the contents of the Excel file inputs/data.xlsx and aggregates the results into a JSON file in outputs/results.json

The format of the Excel file is the following:
Postcode: just a number indicating the postcode	
Sales_Rep_ID: id of the rep sales
Sales_Rep_Name: name of the rep sales
Year: year when the sale was made
Value: the amount of sales

The script must read the Excel file with these columns and prepare the results as aggregates for the Sales Rep. I need to know how much has been sold by each Rep Sales. The result must be saved as a JSON structure in the outputs/results.json file. The format is the following:
{
    "perSale": [
        { "salesRepName": "John", "totalValue": 748299 }, ...
    ]
}

