function nameTemplate(item)
{
  if (item.id)
  {
    var fields = item.text.split('|');
    var born = fields.length > 1 ? '<small class="pull-right text-muted">b.' + fields[1] + '</small>' : '';
    return born + fields[0];
  }
  return item.text
}

function placeTemplate(item)
{
  if (item.id)
  {
    var fields = item.text.split('|');
    return '<span class="location"><img src="/static/people/images/flags/small/' + fields[1] + '.png" class="flag-small"/> ' + fields[0] + '</span>';
  }
  return item.text
}

$(document).ready(function(){
  $.fn.select2.defaults.set('theme', 'bootstrap');
  $.fn.select2.defaults.set('escapeMarkup', function(m){return m;});
  $('#person').select2({templateResult: nameTemplate,
                        templateSelection: nameTemplate}).on('change', function(){window.location = '/person/' + this.value;});
});
