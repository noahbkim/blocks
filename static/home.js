class Block {

    constructor(element) {
        this.element = element;
        this.time = element.innerHTML.trim();
        this.sort = element.sort;
        this.selected = false;
        Block.all.push(this);
    }

    select() {
        this.selected = true;
        this.element.classList.add("selected");
    }

    deselect() {
        this.selected = false;
        this.element.classList.remove("selected");
    }

    toggle() {
        if (this.selected) this.deselect();
        else this.select();
    }

}

Block.all = [];
Block.clearselect = function() {
    for (let block of Block.all)
        block.deselect();
};

class BlockSelection {

    constructor(element) {
        this.element = element;
    }

    update() {
        while (this.element.lastChild)
            this.element.removeChild(this.element.lastChild);
        for (let block of Block.all) {
            if (block.selected) {
                let mini = document.createElement("div");
                mini.classList.add("mini");
                mini.innerHTML = block.time;
                this.element.appendChild(mini);
            }
        }
    }

}

const SHIFT = 16;
const CONTROL = 17;

class BlockManager {

    constructor() {
        this.blocks = [];
        this.selection = new BlockSelection(document.getElementById("selection"));
        this.last = Block.all[0];
        this.modifiers = {shift: false, control: false};
        this.bind();
    }

    bind() {
        let that = this;
        document.addEventListener("keydown", function(e) {
            if (e.keyCode == SHIFT) that.modifiers.shift = true;
            if (e.keyCode == CONTROL) that.modifiers.control = true;
        });
        document.addEventListener("keyup", function(e) {
            if (e.keyCode == SHIFT) that.modifiers.shift = false;
            if (e.keyCode == CONTROL) that.modifiers.control = false;
        });
        for (let block of this.blocks) {
            block.element.addEventListener("click", function() {
                if (that.modifiers.shift) {
                    let start = Block.all.indexOf(block);
                    let end = Block.all.indexOf(that.last);
                    let increment = Math.sign(end - start);
                    for (let i = start; i != end; i += increment) {
                        if (!Block.all[i].selected) Block.all[i].select();
                        else break;
                    }
                } else if (!that.modifiers.control) {
                    Block.clearselect();
                }
                block.select();
                that.last = block;
                that.selection.update();
            });
        }
    }

}

window.onload = function() {

    let manager = new BlockManager();

    let blockElements = document.getElementsByClassName("block");
    for (let i = 0; i < blockElements.length; i++)
        manager.blocks.push(new Block(blockElements[i]));

    manager.bind();

    window.addEventListener("scroll", function(e) {
        editorElement.style.marginTop = document.body.scrollTop + "px";
    });

};
