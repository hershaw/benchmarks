'use strict';

var fs = require('fs')
var moment = require('moment')

var timed = require('./timed').timed

const enforce_number = val => {
  val = parseFloat(val)
  return Number.isNaN(val) ? null : val
}

const enforce_date = (val, format) => {
  val = moment(val, format).valueOf()
  return Number.isNaN(val) ? null : val
}

const enforce_types = index => {
  const len = index.length
  return row => {
    let i = -1
    let col
    while(++i < len) {
      col = index[i]
      if (col.type == 'number')
        row[i] = enforce_number(row[i])
      else if (col.type == 'date')
        row[i] = enforce_date(row[i], col.payload.format)
    }
    return row
  }
}

const apply_index = timed(function apply_index(dodo, index) {
  dodo = dodo.cols(index.map(f => f.name)).map(enforce_types(index))
  fs.writeFileSync(__dirname + '/typed.json', JSON.stringify(dodo.toArray()))
})

module.exports = apply_index
