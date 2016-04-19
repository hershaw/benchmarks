'use strict'

var t = require('transducers.js')
var range = require('lodash/fp/range')

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

module.exports = bin
