"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.optional = void 0;
const composites_1 = require("../composites");
const primitives_1 = require("../primitives");
/**
 * Shorthand for marking a property as optional,
 * this is equivalent to ``t.union([definition, t.undefined()])``.
 *
 * @param definition The type definition to mark as optional.
 */
function optional(definition) {
    return (0, composites_1.union)([definition, (0, primitives_1.undefined)()]);
}
exports.optional = optional;
