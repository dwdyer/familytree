$.tablesorter.addParser(
{id: "names",
 is: function(s){return false;},
 format: function(s){
    var regex = /([\w\s]+)(?:\s\(\w+\))?/g;
    var names = regex.exec(s)[0].trim().split(" ");
    names.splice(0, 0, names[names.length - 1]);
    return names.slice(0, names.length - 1).join(" ");
 },
 type:'text'});

function getSortValue(node) {
  var attr = $(node).attr('data-sort-value');
  return typeof attr !== 'undefined' && attr !== false ? attr : $(node).text();
}
