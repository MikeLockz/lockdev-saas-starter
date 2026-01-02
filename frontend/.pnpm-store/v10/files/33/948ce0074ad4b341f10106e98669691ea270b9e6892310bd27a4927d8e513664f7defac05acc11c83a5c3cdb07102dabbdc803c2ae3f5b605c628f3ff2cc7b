"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.union = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const utils_1 = require("../utils");
/**
 * Describe a type which is one of many
 * options, for example a list of known strings.
 *
 * @example
 * t.type("Size", t.union(["small", "medium", "large"]));
 *
 * @param definitions An array of type definitions.
 */
function union(definitions) {
    return ts.factory.createUnionTypeNode(definitions.map(utils_1.toTypeNode));
}
exports.union = union;
