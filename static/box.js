class Square {
    static getHandleSize() {
        return 10;
    }

    constructor(x, y, width, height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.handleSize = Square.getHandleSize();

        this.isDragging = false;
        this.isResizing = false;
        this.resizeHandle = null;
        this.lastX = 0;
        this.lastY = 0;
    }


    draw(canvas, ctx, img, clear=false) {
        if (clear) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
        }
        ctx.fillStyle = 'transparent';
        ctx.strokeRect(this.x, this.y, this.width, this.height);
        ctx.strokeStyle = 'black';

        // Draw the resize handle
        let handleX = this.x + this.width - this.handleSize;
        let handleY = this.y + this.height - this.handleSize;
        ctx.fillStyle = 'white';
        ctx.fillRect(handleX, handleY, this.handleSize, this.handleSize);
        ctx.strokeStyle = 'black';
        ctx.strokeRect(handleX, handleY, this.handleSize, this.handleSize);
    }


    // Check if the mouse is over the resize handle
    isOverResizeHandle(x, y) {
        let handleX = this.x + this.width - this.handleSize;
        let handleY = this.y + this.height - this.handleSize;
        return x >= handleX && x <= handleX + this.handleSize &&
            y >= handleY && y <= handleY + this.handleSize;
    }
}