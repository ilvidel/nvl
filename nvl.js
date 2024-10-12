/*
const table = document.querySelector('table'); //get the table to be sorted
table.querySelectorAll('th') // get all the table header elements
	.forEach((element, columnNo)=>{ // add a click handler for each
		element.addEventListener('click', event => {
			sortTable(table, columnNo); //call a function which sorts the table by a given column number
		})
	})

function sortTable(table, sortColumn){
	// get the data from the table cells
	const tableBody = table.querySelector('tbody')
	const tableData = table2data(tableBody);
	// sort the extracted data
	tableData.sort((a, b)=>{
		if(a[sortColumn] > b[sortColumn]){
			return 1;
		}
		return -1;
	})
	// put the sorted data back into the table
	data2table(tableBody, tableData);
}
// this function gets data from the rows and cells
// within an html tbody element
function table2data(tableBody){
	const tableData = []; // create the array that'll hold the data rows
	tableBody.querySelectorAll('tr')
		.forEach(row=>{  // for each table row...
			const rowData = [];  // make an array for that row
			row.querySelectorAll('td')  // for each cell in that row
				.forEach(cell=>{
					rowData.push(cell.innerText);  // add it to the row data
				})
			tableData.push(rowData);  // add the full row to the table data
		});
	return tableData;
}

// this function puts data into an html tbody element
function data2table(tableBody, tableData){
	tableBody.querySelectorAll('tr') // for each table row...
		.forEach((row, i)=>{
			const rowData = tableData[i]; // get the array for the row data
			row.querySelectorAll('td')  // for each table cell ...
				.forEach((cell, j)=>{
					cell.innerText = rowData[j]; // put the appropriate array element into the cell
				})
		});
}
*/


/**
 * from w3schools
 */
function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("nvlTable");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;

      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];

      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}