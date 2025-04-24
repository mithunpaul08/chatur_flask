function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Verde Menu')
    .addItem('Retrieve Results from LLMs', 'retrieveResults')
    .addToUi();
}


function retrieveResults() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastRow = 35;
  const startCol = 2; // column B
  const lastCol = sheet.getLastColumn(); // assumes header row is filled with model names

  // Loop through each row (prompt in column A)
  for (let row = 2; row <= lastRow; row++) {
    const prompt = sheet.getRange(row, 1).getValue(); // Column A

    if (!prompt) continue; // skip empty prompts

    // Loop through each model column (B to Z, etc.)
    for (let col = startCol; col <= lastCol; col++) {
      const model = sheet.getRange(1, col).getValue(); // Model name in row 1
      if (!model) continue;

      const response = callPythonScript(prompt, model); // Pass prompt & model
      const cleaned = response.replace(/\n/g, ' ').trim(); // Clean \n
      sheet.getRange(row, col).setValue(cleaned); // Write to cell
    }
  }
}

function callPythonScript(prompt, model) {
  const url = 'https://chaturflask-production.up.railway.app/invoke';

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
