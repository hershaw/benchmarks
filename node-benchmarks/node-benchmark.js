'use strict';

var t = require('transducers.js')
var readline = require('readline')
var fs = require('fs')

var file = fs.createReadStream(__dirname + '/../data/lc_big.csv')

// returns an iteratee function for use in map
function dropFunc(columns, command) {
  var set = new Set(command.payload)
  var i = columns.indexOf(command.name)
  return row => !set.has(row[i])
}

// returns an iteratee function for use in map
function combineFunc(columns, command) {
  var repwith = command.payload.sort().join('_')
  var i = columns.indexOf(command.name)
  var set = new Set(command.payload)
  return row => set.has(row[i]) ? (row[i] = repwith, row) : row
}

var transformCommands = [
   {"type": "combine", "name": "addr_state", "payload": ["CA", "TX"]},
   {"type": "drop", "name": "addr_state", "payload": ["IA", "ME"]},
]
var dropCommand = transformCommands.find(t => t.type == 'drop')
var combineCommand = transformCommands.find(t => t.type == 'combine')

var rl = readline.createInterface({ input: file })
var data = []
rl.on('line', function(line) { data.push(line.split(',')) })
console.time('parseCsv')
file.on('end', function() {
  console.timeEnd('parseCsv')
  var columns = data[0]
  data.splice(0, 1)
  transform(columns, data)
})

function transform(columns, data) {
  console.time('transforms')
  data = t.map(data, combineFunc(columns, combineCommand))
  data = t.filter(data, dropFunc(columns, dropCommand))
  console.timeEnd('transforms')
}
