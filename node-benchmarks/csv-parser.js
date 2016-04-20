var fs = require('fs')
var through = require('through')
var parse = require('csv-parse')

function parseAsPromised(path, delimiter) {
  return new Promise(function(resolve) {
    var file = fs.createReadStream(path)
    var data = []

    var parser = parse({delimiter: delimiter})

    file
      .pipe(parser)
      .pipe(through(function(line) {
        data.push(line)
      }, function() {
        var columns = data[0]
        data.splice(0, 1)
        resolve({data: data, columns: columns})
      }))
  })
}

function parseLazy(path, delimiter) {
  const readerOfLines = require('n-readlines')
  const gen = function * () {
    var liner = new readerOfLines(path)

    var line
    while (line = liner.next()) { // eslint-disable-line no-cond-assign
      yield line.toString('utf8').split(delimiter)
    }
  }

  gen[Symbol.iterator] = function() {
    return this()
  }

  return gen
}

module.exports = {
  parse: parseAsPromised,
  parseLazy: parseLazy
}
