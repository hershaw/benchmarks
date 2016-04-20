'use strict';

var fs = require('fs')
var moment = require('moment')

var timed = require('./timed').timed

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

module.exports = apply_index
