import { ObjectLiteral } from "../typings";
/** Really, it just returns the value you pass */
export declare const getSelf: <T = any>(state: T) => T;
/** Make an object where the keys will have a self getter as value */
export declare const makeSelfGetters: (keys: string[]) => {
    [k: string]: <T = any>(state: T) => T;
};
/** Get 1st/only key of object */
export declare const firstKey: <T extends ObjectLiteral<any>>(obj: T) => keyof T;
/** Get 1st/only prop of object */
export declare const firstProp: <T extends ObjectLiteral<any>>(obj: T) => T[keyof T];
/** Make getter on obj[key] */
export declare const prop: <T extends ObjectLiteral<any>, K extends keyof T>(key: K) => (item: T) => T[K];
//# sourceMappingURL=getters.d.ts.map