'use strict';

var t = require('transducers.js')
var Dodo = require('dodos').default
var parse = require('./csv-parser')

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

const csv = parse(__dirname + '/../data/lc_big.csv', ',')
  .then((result) => {
    transform(result.index, result.data)
  })
  .catch(console.log.bind(console))

function transform(index, data) {
  console.time('node apply transforms')
  let dodo = new Dodo(data, index)
  dodo = dodo.map(combineFunc(index, combineCommand))
  dodo = dodo.filter(dropFunc(index, dropCommand))
  dodo.toArray()
  console.timeEnd('node apply transforms')
}
