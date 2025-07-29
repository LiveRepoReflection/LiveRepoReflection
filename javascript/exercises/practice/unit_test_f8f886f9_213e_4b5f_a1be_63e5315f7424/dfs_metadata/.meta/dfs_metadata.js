class Directory {
  constructor(name) {
    this.name = name;
    this.children = new Map(); // key: child name, value: Directory or File instance
    this.type = 'directory';
  }
}

class File {
  constructor(name, replicationFactor) {
    if (!Number.isInteger(replicationFactor) || replicationFactor <= 0) {
      throw new Error('Invalid replication factor. It must be a positive integer.');
    }
    this.name = name;
    this.replicationFactor = replicationFactor;
    this.size = 0;
    this.type = 'file';
  }
}

class DistributedFileSystem {
  constructor() {
    // Root directory represented as "/"
    this.root = new Directory('');
  }
  
  // Utility: Validate a given absolute path.
  validatePath(path) {
    if (typeof path !== 'string' || !path.startsWith('/')) {
      throw new Error('Path must be a valid absolute path.');
    }
    if (path.length > 1 && path.endsWith('/')) {
      throw new Error('Invalid path format: paths should not end with a forward slash.');
    }
  }
  
  // Utility: Given a path return the node and its parent.
  // If createParentOnly is true, then only traverse to the parent node.
  _traverse(path, getParent = false) {
    this.validatePath(path);
    if (path === '/') {
      return { parent: null, node: this.root, name: '' };
    }
    const parts = path.split('/').filter(Boolean); // remove empty parts
    let current = this.root;
    for (let i = 0; i < parts.length; i++) {
      if (current.type !== 'directory') {
        throw new Error(`Cannot traverse through a non-directory at '${parts.slice(0, i).join('/')}'`);
      }
      // if we are at the immediate parent, return it.
      if (getParent && i === parts.length - 1) {
        return { parent: current, name: parts[i] };
      }
      if (!current.children.has(parts[i])) {
        throw new Error(`The path '/${parts.slice(0, i + 1).join('/')}' does not exist.`);
      }
      current = current.children.get(parts[i]);
    }
    return { parent: null, node: current, name: parts[parts.length - 1] };
  }
  
  createDirectory(path) {
    this.validatePath(path);
    if (path === '/') {
      throw new Error("Root directory '/' already exists.");
    }
    const { parent, name } = this._traverse(path, true);
    if (parent.children.has(name)) {
      throw new Error(`Directory or file '${name}' already exists at the path '${path}'.`);
    }
    // Create new directory and add it to parent children
    const newDir = new Directory(name);
    parent.children.set(name, newDir);
  }
  
  createFile(path, replicationFactor) {
    this.validatePath(path);
    const { parent, name } = this._traverse(path, true);
    if (!parent) {
      throw new Error('Cannot create file at root level without a name.');
    }
    if (parent.children.has(name)) {
      throw new Error(`Directory or file '${name}' already exists at the path '${path}'.`);
    }
    const newFile = new File(name, replicationFactor);
    parent.children.set(name, newFile);
  }
  
  delete(path) {
    this.validatePath(path);
    if (path === '/') {
      throw new Error('Cannot delete root directory.');
    }
    const { parent, name } = this._traverse(path, true);
    if (!parent || !parent.children.has(name)) {
      throw new Error(`The file or directory '${path}' does not exist.`);
    }
    const node = parent.children.get(name);
    if (node.type === 'directory' && node.children.size > 0) {
      throw new Error(`Directory '${path}' is not empty.`);
    }
    parent.children.delete(name);
  }
  
  getFileMetadata(path) {
    this.validatePath(path);
    const { node } = this._traverse(path);
    if (!node || node.type !== 'file') {
      throw new Error(`The file '${path}' does not exist.`);
    }
    return { replicationFactor: node.replicationFactor, size: node.size };
  }
  
  listFiles(path) {
    this.validatePath(path);
    const { node } = this._traverse(path);
    if (!node || node.type !== 'directory') {
      throw new Error(`The directory '${path}' does not exist.`);
    }
    return Array.from(node.children.keys());
  }
  
  increaseFileSize(path, increment) {
    if (typeof increment !== 'number' || increment < 0) {
      throw new Error('Increment must be a non-negative number.');
    }
    this.validatePath(path);
    const { node } = this._traverse(path);
    if (!node || node.type !== 'file') {
      throw new Error(`The file '${path}' does not exist.`);
    }
    node.size += increment;
  }
  
  findFilesWithReplicationFactor(replicationFactor) {
    if (!Number.isInteger(replicationFactor) || replicationFactor <= 0) {
      throw new Error('Invalid replication factor. It must be a positive integer.');
    }
    const result = [];
    const traverseTree = (current, currentPath) => {
      if (current.type === 'file') {
        if (current.replicationFactor === replicationFactor) {
          result.push(currentPath);
        }
      } else if (current.type === 'directory') {
        current.children.forEach((child, name) => {
          const childPath = currentPath === '/' ? `/${name}` : `${currentPath}/${name}`;
          traverseTree(child, childPath);
        });
      }
    };
    traverseTree(this.root, '/');
    return result;
  }
}

module.exports = {
  DistributedFileSystem
};