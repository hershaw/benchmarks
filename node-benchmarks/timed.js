'use strict'

const fs = require('fs')

const times = []

function timed(fn) {
  return function(arg1, arg2, arg3) {
    const start = process.hrtime()
    const ret = fn(arg1, arg2, arg3)
    const diff = process.hrtime(start)
    times.push([fn.name, diff[0] + diff[1] / 1e9])
    return ret
  }
}

function getTimes() {
  return times
}

function saveTimes() {
  const args = [].slice.call(arguments)
  const str = times.map(time => time[1]).join('\n')
  fs.writeFileSync('./timings/' + args.join('-'), str + '\n')
}

module.exports = {
  timed: timed,
  getTimes: getTimes,
  saveTimes: saveTimes
}
