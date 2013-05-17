function Key() {
  var showing = "product",
    classification = "hs4";
    
  function key(selection) {
    selection.each(function(attrs, i) {
      
      // unique list of categories
      cats = pretty_cats(attrs);
      sitcs = pretty_sitcs(attrs);
      
      if (prod_class == "sitc4" && (app_type=="casy"||app_type=="ccsy")){
        d3.select(this)
          .attr("id", "sitc1")
          .selectAll("a").data(d3.values(sitcs))
          .enter()
            .append("a")
            .call(key_icon)
      }
      else 
      {
      d3.select(this)
        .attr("id", classification)
        .selectAll("a").data(d3.values(cats))
        .enter()
          .append("a")
          .call(key_icon)
      }
      // put tooltip on mouseover
      $('#key a').tipsy({"gravity":'s',"fade":true});      
    })
  }
  
  ////////////////////////////////////////////
  // PRIVATE functions for this app shhhhh...
  ////////////////////////////////////////////
  
  // Find the unique categories from list of attributes
  function pretty_cats(attrs){
    cats = {}
    d3.values(attrs).forEach(function(d){
      cats[d.category_id] = {}
      d3.keys(d).forEach(function(dd){
        if(dd.indexOf("category") > -1){
          cats[d.category_id][dd.replace("category_", "")] = d[dd]
        }
      })
    })
    return cats
  }
  
  // Find the unique categories from list of attributes
  function pretty_sitcs(attrs){
    sitcs = {}
    d3.values(attrs).forEach(function(d){
 
      sitcs[d.sitc1_id] = {}
      d3.keys(d).forEach(function(dd){
        
        if(dd.indexOf("sitc1") > -1){
          sitcs[d.sitc1_id][dd.replace("sitc1_", "")] = d[dd]
        }      
      })
    })
    return sitcs
  }
  
  
  // Format the anchor how we want for the given category
  function key_icon(a){
    a.attr("title", function(d){ return d.name; })
    // .attr("class", function(d){ return showing + " cat_"+d.id; })
    // depending on whether we're showing products or countries
    // show icons or just text of that region
    if(showing == "product"){
      a.attr("class", function(d){ return showing + " cat_"+d.id; })
      a.append("img")
        .attr("src", function(d){
          return "/media/img/icons/community_"+d.id+".png"
        })
    }
    else {
       a.style("background", function(d){ return d.color; })
        .attr("class", function(d){ return showing + " cat_"+d.id+" "+d.continent; })
        .text(function(d){ return name(d.name);})
    }
    // mouseover events (extends the specific apps highlight funciton)
    a.on("mouseover", function(d){
        console.log(d);
        // d3.select("#viz").call(viz.solo([d.name]));
        // d3.select("#viz").call(viz.highlight(d.id));
      })
      .on("mouseout", function(d){
        // d3.select("#viz").call(viz.solo([]));
        // d3.select("#viz").call(viz.highlight(null));
      })
    a.on("click", function(d){
      // If this node is already selected, return to unsorted
      console.log(d3.select(this))
      if (d3.select(this).attr("active") == "true")
      {
        d3.select("#viz").call(viz.solo([]));
        d3.select(this).attr("active","false");
        d3.selectAll("."+d.continent).attr("active","false");
        d3.selectAll(".key a").style("opacity","1")
                              .style("pointer-events","auto")  
                              .style("cursor","");    
      }
      // Otherwise, we need to filter just this community
      // by using VizWiz soloing functionality 
      else
      {
        // Grey out the other communities
        d3.selectAll(".key a").style("opacity",".1")
                              .style("pointer-events","none")
                              .style("cursor","default");
        
        // Now we'll keep our selection highlighted
        // Check to see app is display country info, in which case
        // we need filter by continent              
        if (d.continent != undefined){
          // If this is a continent, we want to select all the regions
          d3.selectAll("."+d.continent).style("opacity","1")
                                   .style("pointer-events","auto")  
                                   .style("cursor","")                 
                                   .attr("active","true"); 
          
          app_name=="stacked" ? stack_solo_filter(d.continent) : d3.select("#viz").call(viz.solo([d.continent]));
          // d3.select("#viz").call(viz.solo([d.continent]));
        }
        // or we can simply filter by product community name
        else 
        {
          d3.select(this).style("opacity","1")
                         .style("pointer-events","auto")  
                         .style("cursor","")                 
                         .attr("active","true"); 
                         
          app_name=="stacked" ? stack_solo_filter(d.name) : d3.select("#viz").call(viz.solo([d.name]));
          
        }              
                       
      }
        
    }) 
    
    a.style("border",function(d){
      if (d.name == "X"){
        return "1px solid red";
      }
      
    })
     
  }
  
  
  // HELPER FUNCTION to shorten names so they fit on one line
  // totally for aesthetics braaaaaa....
  function name(long_name){
    var short_name = long_name;
    short_name = short_name.replace("South-Eastern", "SE")
    short_name = short_name.replace("Eastern", "E")
    short_name = short_name.replace("Northern", "N")
    short_name = short_name.replace("Southern", "S")
    short_name = short_name.replace("South", "S")
    short_name = short_name.replace("Western", "W")
    short_name = short_name.replace("Central", "C")
    return short_name;
  }
  
  function stack_solo_filter(name){
      var nest_level = ($("#nesting_level").val());
      var use_this
      if (nest_level == "nest0"){
        //if we're display countries sort by 2nd tier 
        (app_type=="csay"||app_type=="ccsy"||app_type=="sapy") ? 
        use_this = nest1_value : use_this = nest0_value
      } else if(nest_level == "nest1"){ 
        use_this = nest1_value  
      } else { 
        use_this = nest2_value } 
        
      var solos = []
      use_this.forEach(function(d){
        if (d.nesting_0.name == name){
         solos.push(d.name)
       } 
      });
      unq = solos.getUnique();
      console.log(unq)
      d3.select("#viz").call(viz.solo(unq));  
  }
  ////////////////////////////////////////////
  // PUBLIC getter / setter functions
  ////////////////////////////////////////////
  key.showing = function(value) {
    if (!arguments.length) return showing;
    showing = value;
    return key;
  };
  
  key.classification = function(value) {
    if (!arguments.length) return classification;
    classification = value;
    return key;
  };
  
  /////////////////////////////////////////////////////////////////////
  // BE SURE TO ALWAYS RETURN THE APP TO ALLOW FOR METHOD CHAINING
  ///////////////////////////////////////////////////////////////////// 
  return key;
}