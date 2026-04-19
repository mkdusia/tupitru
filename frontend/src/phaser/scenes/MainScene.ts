import Phaser from 'phaser'

export default class MainScene extends Phaser.Scene {
    constructor() {
        super('MainScene');
    }

    preload() : void {

    }

    create() : void {
        this.add.text(300, 300, 'Phaser is Running!', { color: '#0f0' });
    }
}