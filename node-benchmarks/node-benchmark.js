'use strict';

var fs = require('fs')
var moment = require('moment')
var sampleSize = require('lodash/fp/sampleSize')
var Dodo = require('dodos').default

var parse = require('./csv-parser').parse
var bin = require('./bin')

var timed = require('./timed').timed
var saveTimes = require('./timed').saveTimes

const argv = process.argv.slice(2)
const filepath = argv[0]
const transform_set = argv[1]
const action = argv[2]
const iters = +argv[3]
if (!transform_set || ['small', 'medium', 'big'].indexOf(transform_set) == -1)
  throw new Error('unrecognised transform_set: ' + transform_set)

var index = require('../index.json')

if (action == 'apply_index') {
  parse(__dirname + '/../data/' + filepath + '.csv', ',')
    .then(result => {
      apply_index(new Dodo(result.data, result.columns), index)
      saveTimes(filepath, transform_set)
    })
    .catch(console.log.bind(console))
} else if (action == 'get_cols') {
  const transforms = require('../transforms.json')
  const dodo = new Dodo(require('./typed.json'), index.map(f => f.name))

  let i = -1
  while (++i < iters) {
    get_cols(dodo, transforms[transform_set], sampleSize(5, index))
  }

  saveTimes(filepath, transform_set)
} else if (action == 'calculate_stats') {
  const transforms = require('../transforms.json')
  const dodo = new Dodo(require('./typed.json'), index.map(f => f.name))

  let i = -1
  while (++i < iters) {
    calculate_stats(dodo, transforms[transform_set], sampleSize(5, index))
  }

  saveTimes(filepath, transform_set, action)
}

const apply_index = timed(function apply_index(dodo, index) {
  dodo = dodo.cols(index.map(f => f.name))

  const len = index.length
  dodo = dodo.map(row => {
    let i = -1
    let col
    while(++i < len) {
      col = index[i]
      if (col.type == 'category') {
        continue
      } else if (col.type == 'number') {
        const val = parseFloat(row[i])
        row[i] = Number.isNaN(val) ? null : val
      } else if (col.type == 'date') {
        const val = moment(row[i], col.payload.format).valueOf()
        row[i] = Number.isNaN(val) ? null : val
      }
    }
    return row
  })

  fs.writeFileSync(__dirname + '/typed.json', JSON.stringify(dodo.toArray()))
})

// returns an iteratee function for use in filter
function dropFunc(dodo, command) {
  var set = new Set(command.payload)
  const i = dodo.index[command.name]
  return row => !set.has(row[i])
}

// returns an iteratee function for use in map
function combineFunc(dodo, command) {
  var repwith = command.payload.sort().join('_')
  var set = new Set(command.payload)
  const i = dodo.index[command.name]
  return row => {
    if (set.has(row[i]))
      row[i] = repwith
    return row
  }
}

function apply_transforms(dodo, transforms) {
  for (const t of transforms) {
    if (t.type == 'drop') {
      dodo = dodo.filter(dropFunc(dodo, t))
    } else if (t.type == 'combine') {
      dodo = dodo.map(combineFunc(dodo, t))
    }
  }
  return dodo
}

const get_cols = timed(function get_cols(dodo, transforms, index) {
  dodo = apply_transforms(dodo, transforms)

  dodo.cols(index.map(f => f.name)).toArray()
})

const calculate_stats = timed(function calculate_stats(dodo, transforms, index) {
  console.log(dodo.length)
  dodo = apply_transforms(dodo, transforms)
  console.log(dodo.length)
  dodo = new Dodo(dodo.toArray(), dodo.index)

  const stats = dodo
    .cols(index.filter(f => f.type == 'number').map(f => f.name))
    .stats('min', 'max', 'mean')

  for (const col of index) {
    if (col.type == 'number') {
      const s = stats[col.name]
      stats[col.name] = {
        min: s[0],
        max: s[1],
        mean: s[2],
        hist: bin(dodo.col(col.name).toArray(), 30)
      }
    } else if (col.type == 'category') {
      const uniques = [...dodo.col(col.name).groupBy().count().entries()]
      stats[col.name] = {
        uniques: uniques,
        uniqCount: uniques.length
      }
    }
  }

  return stats
})
