import { ObjectLiteral, PrimitiveValue } from "../typings";
/**
 * Return the difference between left in right
 * @example getDiff([1, 2, 3], [1, 4, 5]) -> [2, 3]
 */
export declare const getDiff: <T = any>(left: T[], right: T[]) => T[];
/**
 * Return the difference between left in right / right in left
 * @example getSymmetricDiff([1, 2, 3], [1, 4, 5]) -> [2, 3, 4, 5]
 */
export declare const getSymmetricDiff: <T = any>(left: T[], right: T[]) => T[];
/**
 * Return the union between left & right
 * @example getUnion([1, 2, 3], [1, 4, 5]) -> [1, 2, 3, 4, 5]
 */
export declare const getUnion: <T = any>(left: T[], right: T[]) => T[];
/**
 * Return the intersection between left & right
 * @example getUnion([1, 2, 3], [1, 4, 5]) -> [1]
 */
export declare const getIntersection: <T = any>(left: T[], right: T[]) => T[];
/**
 * Checks that all items (right) are in left array
 * @example hasAll([1, 2, 3], [1, 4, 5]) = false
 * @example hasAll([1, 2, 3, 4, 5], [1, 4, 5]) = true
 */
export declare const hasAll: <T = any>(inArray: T[], items: T[]) => boolean;
/**
 * Return uniques/de-duplicated values in array
 * @example uniques([1, 2, 3, 4, 5].concat([6, 7, 1, 2, 9])) // = [1, 2, 3, 4, 5, 6, 7, 9]
 */
export declare const uniques: <T = any>(arr: T[]) => T[];
/** Return uniques/de-duplicated values in array of objects using the given propPath as unique identifier */
export declare const uniquesByProp: <T = any>(arr: T[], propPathOrGetter: string | ((value: T) => any)) => T[];
/** Exclude items in array */
export declare const exclude: <T = any>(arr: T[], excluded: T[]) => T[];
/** Find an item/index from its value using a property path in the array (can be nested using a dot delimited syntax) */
export declare const findBy: <K extends (string & {}) | keyof Item, Item = any, ValueEqualsTo = any, ByIndex extends boolean = undefined>(arr: Item[], path: K, value: ValueEqualsTo, index?: ByIndex) => ByIndex extends undefined ? Item : ByIndex extends true ? number : Item;
export declare function findRight<Item, As extends Item>(arr: Item[], predicate: (item: Item) => item is As): As;
export type SortDirection = "asc" | "desc";
export declare const compareBasic: (a: number, b: number) => 1 | -1 | 0;
/** Sort an array of objects by a common prop key (or dot-delimited path) in given direction (asc|desc, defaults to asc) */
export declare function sortBy<T extends ObjectLiteral, K extends keyof T | (string & {})>(arr: T[], key: K, dir?: SortDirection): T[];
/** Compare (to sort) 2 objects by a common prop key (or dot-delimited path) in given direction (asc|desc, defaults to asc) */
export declare function sortCompareFn<T, K extends keyof T | (string & {})>(left: T, right: T, key: K, dir?: SortDirection): number;
/** Compare arrays & return true if all members are included (order doesn't matter) */
export declare function isEqualArrays(arr1: PrimitiveValue[], arr2: PrimitiveValue[]): boolean;
/** Combine one or more array into the first one while pushing only distinct unique values */
export declare const combineUniqueValues: <T extends PrimitiveValue>(arr1?: T[], ...arr2: T[][]) => T[];
/** Combine one or more array of objects into the first one while pushing only distinct unique objects using the given propPath as unique identifier */
export declare const combineUniqueValuesByProps: <T extends ObjectLiteral<any> = any>(arrays: T[][], propPath: string) => T[];
/** Get first item of array */
export declare const first: <T>(value: T[]) => T;
/** Get last item of array */
export declare const last: <T>(value: T[]) => T;
/** Polyfill Array.flatMap */
export declare function flatMap<T, U>(array: T[], callbackfn: (value: T, index: number, array: T[]) => U[]): U[];
/** Make an array of {count} empty elements */
export declare const makeArrayOf: (count: number) => any[];
/** Split an array in chunk of given size */
export declare const chunk: <T = any>(arr: T[], size: number) => T[][];
/** Array of picked property */
export declare const pluck: <K extends keyof T, T extends object>(arr: T[], prop: K) => T[K][];
export declare const prependItem: <T>(array: T[], item: T) => T[];
export declare const appendItem: <T>(array: T[], item: T) => T[];
export declare const updateItem: <T extends ObjectLiteral<any>>(array: T[], idPath: string, update: T) => T[];
export declare const removeValue: <T>(array: T[], item: T) => T[];
export declare const removeValueMutate: <T>(array: T[], item: T) => T[];
export declare const removeItem: <T>(array: T[], idPath: string, value: any) => T[];
export declare const removeItemMutate: <T>(array: T[], idPath: string, value: any) => T[];
export declare const updateAtIndex: <T>(array: T[], index: number, update: T) => T[];
export declare const removeAtIndex: <T>(array: T[], index: number) => T[];
export declare const removeAtIndexMutate: <T>(array: T[], index: number) => T[];
export declare function getPrevItem<T>(array: T[], index: number, loop?: boolean, step?: number): T;
export declare function getNextItem<T>(array: T[], index: number, loop?: boolean, step?: number): T;
/**
 * Get the next index based on the current index and step.
 *
 * @param currentIndex the current index
 * @param length the total length or count of items
 * @param step the number of steps
 * @param loop whether to circle back once `currentIndex` is at the start/end
 */
export declare function getNextIndex(currentIndex: number, length: number, loop?: boolean, step?: number): number;
/**
 * Get's the previous index based on the current index.
 * Mostly used for keyboard navigation.
 *
 * @param index - the current index
 * @param length - the length or total length of items in the array
 * @param loop - whether we should circle back to the
 * first/last once `currentIndex` is at the start/end
 */
export declare function getPrevIndex(index: number, length: number, loop?: boolean, step?: number): number;
/** Sort array of object by given prop using a reference order array, sort items not in reference order in lasts positions */
export declare const sortArrayOfObjectByPropFromArray: <T extends ObjectLiteral<any>, K extends (string & {}) | keyof T>(arr: T[], prop: K, orderedProp: T[K][]) => T[];
/** Sort array of object by given prop using a reference order array, sort items not in reference order in lasts positions */
export declare const sortListFromRefArray: <T extends string | number>(arr: T[], orderedProp: T[]) => T[];
export declare const castAsArray: <T>(value: T | T[]) => T[];
//# sourceMappingURL=array.d.ts.map