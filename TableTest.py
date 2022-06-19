from ij.measure import ResultsTable

table = ResultsTable()
table.setColumn("Test", [])
table.setColumn("Test2", [])
table.setColumn("Test3", [])
table.incrementCounter()
table.addValue("Test", "Spot 1")
table.incrementCounter()
table.addValue(1, 8)
table.show("Test")