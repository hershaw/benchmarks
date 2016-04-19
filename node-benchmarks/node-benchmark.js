'use strict';

var moment = require('moment')
var t = require('transducers.js')
var range = require('lodash/fp/range')
var Dodo = require('dodos').default
var parse = require('./csv-parser')

const argv = process.argv.slice(2)
if (!argv[0] || ['small', 'medium', 'big'].indexOf(argv[0]) == -1)
  throw new Error('unrecognised arg: ' + argv[0])

const transform_set = argv[0]

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

var index = require('../index.json')
var transforms = require('../transforms.json')

parse(__dirname + '/../data/lc_big.csv', ',')
  .then(result => {
    let dodo = new Dodo(result.data, result.columns)
    dodo = apply_index(dodo)
    dodo = apply_transforms(dodo, transform_set)
    calculate_stats(dodo)
  })
  .catch(console.log.bind(console))

function apply_index(dodo) {
  console.time('apply index')

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
        // const val = moment(row[i], col.payload.format).valueOf()
        // row[i] = Number.isNaN(val) ? null : val
      }
    }
    return row
  })

  console.timeEnd('apply index')
  return dodo
}

function apply_transforms(dodo, benchmark) {
  console.time('apply transforms: ' + benchmark)

  for (const t of transforms[benchmark]) {
    if (t.type == 'drop')
      dodo = dodo.filter(dropFunc(dodo, t))
    else if (t.type == 'combine')
      dodo = dodo.map(combineFunc(dodo, t))
  }

  console.timeEnd('apply transforms: ' + benchmark)

  return dodo
}

function calculate_stats(dodo) {
  console.time('calc stats')
  console.time('materialize')
  dodo = new Dodo(dodo.toArray(), dodo.index)
  console.timeEnd('materialize')
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
  console.timeEnd('calc stats')
  return stats
}

function bin(series, nrOfBins, extent) {
  series = t.filter(
    series,
    extent
      ? v => Number.isFinite(v) && v <= extent[1] && v >= extent[0]
      : Number.isFinite
  )

  // copy the series before because sort acts inplace
  series = [...series]
  series.sort((a, b) => a - b)

  let len = series.length
  let seriesMin = series[0]
  let seriesMax = series[len - 1]

  const binWidth = (seriesMax - seriesMin) / nrOfBins

  let bins = t.map(
    range(0, nrOfBins),
    i => {
      const isLastBin = i === nrOfBins - 1
      const binMin = seriesMin + i * binWidth
      const binMax = isLastBin ? seriesMax : binMin + binWidth
      return {
        min: binMin,
        max: binMax,
        mid: (binMin + binMax) / 2,
        count: 0
      }
    }
  )

  let seriesIndex = 0
  let binIndex = 0
  while (seriesIndex++ < len) {
    let item = series[seriesIndex]
    while(item > bins[binIndex].max) {
      ++binIndex
    }
    bins[binIndex].count++
  }

  return bins
}
