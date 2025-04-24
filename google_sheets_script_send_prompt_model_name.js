function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Verde Menu')
    .addItem('Retrieve Results from LLMs', 'retrieveResults')
    .addToUi();
}

function retrieveResults() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastRow = 35;
  const startCol = 3; // column C
  const lastCol = sheet.getLastColumn(); // assumes header row is filled with model names

  // Loop through each row (prompt in column A)
  for (let row = 2; row <= lastRow; row++) {
    let prompt = sheet.getRange(row, 1).getValue(); // Column A
    const comparisonValue = sheet.getRange(row, 2).getValue(); // Column B

    if (!prompt || !comparisonValue) continue; // skip if prompt or comparison value is empty

    // Append the comparison value to the prompt
    prompt += ` Compare your answer with the gold answer that ${comparisonValue} and give me a semantic overlap percentage value.`;

    // Loop through each model column (C onwards)
    for (let col = startCol; col <= lastCol; col++) {
      const model = sheet.getRange(1, col).getValue(); // Model name in row 1
      if (!model) continue;

      try {
        const response = callPythonScript(prompt, model); // Pass modified prompt & model
        const cleaned = response.replace(/\n/g, ' ').trim(); // Clean \n
        sheet.getRange(row, col).setValue(cleaned); // Write full response to cell

        // Extract semantic overlap percentage
        const percentageMatch = cleaned.match(/(\d+(\.\d+)?)%/);
        const percentage = percentageMatch ? percentageMatch[1] : "error";
        sheet.getRange(3, col).setValue(percentage); // Write percentage to row 3
      } catch (error) {
        sheet.getRange(row, col).setValue("error"); // Write "error" to cell if an exception occurs
        sheet.getRange(3, col).setValue("error"); // Write "error" to row 3 if an exception occurs
      }
    }
  }
}

function callPythonScript(prompt, model) {
  // one which takes both model and prompt  : https://web-production-ffdbc.up.railway.app/invoke
  // one which takes only  prompt  : https://chaturflask-production.up.railway.app/invoke
  const url = 'https://web-production-ffdbc.up.railway.app/invoke';

  const payload = {
    prompt: prompt,
    model: model
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload)
  };

  const response = UrlFetchApp.fetch(url, options);
  const json = JSON.parse(response.getContentText());

  return json.response || "No response";
}