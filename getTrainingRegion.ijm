run("Enhance Contrast", "saturated=0.35");
makeRectangle(200, 200, 768, 768);
waitForUser("Move rectangle to select a training region...");
run("Crop");
run("Split Channels");