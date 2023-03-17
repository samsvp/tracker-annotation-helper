class Square {
    constructor(x, y, width, height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;

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
        let handleSize = 10;
        let handleX = this.x + this.width - handleSize;
        let handleY = this.y + this.height - handleSize;
        ctx.fillStyle = 'white';
        ctx.fillRect(handleX, handleY, handleSize, handleSize);
        ctx.strokeStyle = 'black';
        ctx.strokeRect(handleX, handleY, handleSize, handleSize);
    }


    // Check if the mouse is over the resize handle
    isOverResizeHandle(x, y) {
        let handleSize = 10;
        let handleX = this.x + this.width - handleSize;
        let handleY = this.y + this.height - handleSize;
        return x >= handleX && x <= handleX + handleSize &&
            y >= handleY && y <= handleY + handleSize;
    }
}