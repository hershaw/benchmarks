var readline = require('readline')
var fs = require('fs')

function parse(path, delimiter) {
  return new Promise(function(resolve) {
    var file = fs.createReadStream(path)
    var rl = readline.createInterface({ input: file })
    var data = []

    rl.on('line', function(line) {
      data.push(line.split(delimiter))
    })

    file.on('end', function() {
      var columns = data[0]
      data.splice(0, 1)
      resolve({data: data, columns: columns})
    })
  })
}

module.exports = parse
