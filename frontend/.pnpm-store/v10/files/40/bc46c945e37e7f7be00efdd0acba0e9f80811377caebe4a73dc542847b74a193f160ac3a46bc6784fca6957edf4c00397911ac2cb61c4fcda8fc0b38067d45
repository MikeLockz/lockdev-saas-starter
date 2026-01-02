"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.intersection = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const utils_1 = require("../utils");
/**
 * @param definitions An array of type definitions.
 */
function intersection(definitions) {
    return ts.factory.createIntersectionTypeNode(definitions.map(utils_1.toTypeNode));
}
exports.intersection = intersection;
