"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.interface = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const utils_1 = require("../../utils");
const utils_2 = require("../utils");
/**
 * Constructs an interface with the given name and properties.
 */
function constructInterface(name, properties) {
    return ts.factory.createInterfaceDeclaration(undefined, [ts.factory.createModifier(ts.SyntaxKind.ExportKeyword)], name, undefined, undefined, Object.entries(properties).map(([key, node]) => {
        return (0, utils_2.typeProperty)(key, node);
    }));
}
/**
 * Create an interface. Used to describe the shape
 * of objects, and can be extended by others.
 *
 * @param name The name of the interface.
 * @param properties An object, with type definitions as values or a function which lazily returns them.
 */
function interface_(name, properties) {
    if (typeof properties !== "function")
        return constructInterface(name, properties);
    return (0, utils_1.setLazy)(constructInterface(name, {}), () => constructInterface(name, properties()));
}
exports.interface = interface_;
