'use strict';

var timed = require('./timed').timed
var apply_transforms = require('./apply_transforms')

const get_cols = timed(function get_cols(dodo, transforms, index) {
  dodo = apply_transforms(dodo, transforms)

  dodo.cols(index.map(f => f.name)).toArray()
})

module.exports = get_cols
