"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.runtimeLiteral = exports.runtimeProperty = exports.runtimeReference = exports.toRuntimeNode = exports.isRuntimeDefinition = exports.isRuntimeDefinitionObject = exports.isReferenceLike = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const utils_1 = require("../utils");
function isReferenceLike(value) {
    return (0, utils_1.isNode)(value) && (ts.isEnumDeclaration(value) || ts.isVariableStatement(value));
}
exports.isReferenceLike = isReferenceLike;
function isRuntimeDefinitionObject(object) {
    if (typeof object !== "object" || !object)
        return false;
    for (const value of Object.values(object)) {
        if (!isRuntimeDefinition(value))
            return false;
    }
    return true;
}
exports.isRuntimeDefinitionObject = isRuntimeDefinitionObject;
function isRuntimeDefinition(value) {
    return isReferenceLike(value) || isRuntimeDefinitionObject(value) || (0, utils_1.isPrimitive)(value);
}
exports.isRuntimeDefinition = isRuntimeDefinition;
function toRuntimeNode(definition, reference = true) {
    if (reference && isReferenceLike(definition))
        return runtimeReference(definition);
    return (0, utils_1.isNode)(definition) ? definition : runtimeLiteral(definition);
}
exports.toRuntimeNode = toRuntimeNode;
function runtimeReference(definition) {
    const name = ts.isVariableStatement(definition)
        ? definition.declarationList.declarations[0].name.text
        : definition.name.text;
    return ts.factory.createIdentifier(name);
}
exports.runtimeReference = runtimeReference;
/**
 * Create a property signature, this is primarily used
 * internally and does not have much usage outside of that.
 *
 * @param name The property name.
 * @param definition The type definition.
 */
function runtimeProperty(name, definition) {
    var _a;
    const node = toRuntimeNode(definition);
    const propertyComments = (_a = ts.getSyntheticLeadingComments(node)) !== null && _a !== void 0 ? _a : [];
    if (propertyComments.length !== 0)
        ts.setSyntheticLeadingComments(node, []);
    const tsPropertySignature = ts.factory.createPropertyAssignment(runtimeLiteral(name), node);
    return propertyComments.length !== 0
        ? ts.setSyntheticLeadingComments(tsPropertySignature, propertyComments)
        : tsPropertySignature;
}
exports.runtimeProperty = runtimeProperty;
function runtimeLiteral(definition) {
    if (typeof definition === "string")
        return ts.factory.createStringLiteral(definition);
    if (typeof definition === "number")
        return ts.factory.createNumericLiteral(definition);
    if (typeof definition === "boolean")
        return (definition ? ts.factory.createTrue : ts.factory.createFalse)();
    if (typeof definition === "bigint")
        return ts.factory.createBigIntLiteral(definition.toString());
    return ts.factory.createObjectLiteralExpression(Object.entries(definition).map(([key, node]) => {
        return runtimeProperty(key, node);
    }), true);
}
exports.runtimeLiteral = runtimeLiteral;
