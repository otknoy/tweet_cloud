var filename = 'data/data.csv';

d3.csv(filename, function(data){
    data = data.splice(0, 1000);

    var width = 1024;
    var height = 768;
    var fill = d3.scale.category20();

    var wordcount = data.map(function(d) {
	return {
	    text: d.word,
	    // size: Math.pow(d.count/2, 1.1)//2*Math.pow(d.count, 1.4)
	    size: 3*Math.pow(d.count, 1.2)
	};
    });

    d3.layout.cloud().size([width, height])
        .words(wordcount)
        .padding(5)
        .rotate(function() { return 10-20*Math.random();})//~~(Math.random() * 2) * 90; })
        // .rotate(function() { return 0;})//~~(Math.random() * 2) * 90; })
        .font("Impact")
        .fontSize(function(d) { return d.size; })
        .on("end", draw)
        .start();

    function draw(words) {
        d3.select("body").append("svg")
            .attr({
		"width": width,
		"height": height
            })
            .append("g")
            .attr("transform", "translate(" + [ width >> 1, height >> 1 ] + ")")
            .selectAll("text")
            .data(words)
            .enter()
            .append("text")
            .style({
		"font-size": function(d) { return d.size + "px"; },
		"font-family": "Impact",
		"fill": function(d, i) { return fill(i); }
            })
            .attr({
		"text-anchor": "middle",
		"transform": function(d) { return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")"; }
            })
            .text(function(d) { return d.text; });
    }
});