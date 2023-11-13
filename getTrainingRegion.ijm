run("Enhance Contrast", "saturated=0.35");
makeRectangle(200, 200, 824, 824);
waitForUser("Move rectangle to select a training region...");
run("Crop");
run("Split Channels");