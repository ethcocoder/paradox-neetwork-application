declare module 'expo-asset' {
    export class Asset {
        static fromModule(module: any): Asset;
        downloadAsync(): Promise<this>;
        localUri: string | null;
        uri: string;
        name: string;
        type: string;
        hash: string | null;
        width: number | null;
        height: number | null;
    }
}
