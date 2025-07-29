const { DistributedFileSystem } = require('./dfs_metadata');

describe('DistributedFileSystem', () => {
  let dfs;
  beforeEach(() => {
    dfs = new DistributedFileSystem();
  });

  test('should successfully create directories and files', () => {
    // Create directories
    dfs.createDirectory("/home");
    dfs.createDirectory("/home/user");
    expect(dfs.listFiles("/home")).toContain("user");

    // Create a file
    dfs.createFile("/home/user/document.txt", 3);
    const metadata = dfs.getFileMetadata("/home/user/document.txt");
    expect(metadata).toHaveProperty("replicationFactor", 3);
    expect(metadata).toHaveProperty("size", 0);

    // List files in a directory
    const userList = dfs.listFiles("/home/user");
    expect(userList).toContain("document.txt");
  });

  test('should increase file size correctly', () => {
    dfs.createDirectory("/files");
    dfs.createFile("/files/log.txt", 2);
    dfs.increaseFileSize("/files/log.txt", 2048);
    const metadata = dfs.getFileMetadata("/files/log.txt");
    expect(metadata.size).toBe(2048);
  });

  test('should throw error when creating a file in a non-existent directory', () => {
    expect(() => {
      dfs.createFile("/invalid/document.txt", 2);
    }).toThrow();
  });

  test('should throw error when creating a directory that already exists', () => {
    dfs.createDirectory("/data");
    expect(() => {
      dfs.createDirectory("/data");
    }).toThrow();
  });

  test('should throw error when creating a file that already exists', () => {
    dfs.createDirectory("/data");
    dfs.createFile("/data/file.txt", 1);
    expect(() => {
      dfs.createFile("/data/file.txt", 1);
    }).toThrow();
  });

  test('should throw error for invalid replication factor', () => {
    dfs.createDirectory("/media");
    expect(() => {
      dfs.createFile("/media/movie.mp4", 0);
    }).toThrow();
    expect(() => {
      dfs.createFile("/media/song.mp3", -2);
    }).toThrow();
  });

  test('should throw error when deleting a non-empty directory', () => {
    dfs.createDirectory("/projects");
    dfs.createDirectory("/projects/app");
    dfs.createFile("/projects/app/index.js", 2);
    expect(() => {
      dfs.delete("/projects/app");
    }).toThrow();
  });

  test('should delete files and directories properly', () => {
    dfs.createDirectory("/var");
    dfs.createDirectory("/var/logs");
    dfs.createFile("/var/logs/error.log", 1);
    // Delete file successfully
    dfs.delete("/var/logs/error.log");
    expect(dfs.listFiles("/var/logs")).not.toContain("error.log");

    // Now delete empty directory
    dfs.delete("/var/logs");
    const varContents = dfs.listFiles("/var");
    expect(varContents).not.toContain("logs");
  });

  test('should list files correctly in a directory', () => {
    dfs.createDirectory("/workspace");
    dfs.createFile("/workspace/a.txt", 1);
    dfs.createFile("/workspace/b.txt", 2);
    dfs.createDirectory("/workspace/subdir");
    const list = dfs.listFiles("/workspace");
    expect(list.sort()).toEqual(["a.txt", "b.txt", "subdir"].sort());
  });

  test('should update file size incrementally', () => {
    dfs.createDirectory("/logs");
    dfs.createFile("/logs/app.log", 3);
    dfs.increaseFileSize("/logs/app.log", 100);
    dfs.increaseFileSize("/logs/app.log", 150);
    const metadata = dfs.getFileMetadata("/logs/app.log");
    expect(metadata.size).toBe(250);
  });

  test('should find files with the specified replication factor', () => {
    dfs.createDirectory("/files");
    dfs.createFile("/files/a.txt", 2);
    dfs.createFile("/files/b.txt", 3);
    dfs.createDirectory("/files/sub");
    dfs.createFile("/files/sub/c.txt", 2);
    let found = dfs.findFilesWithReplicationFactor(2);
    expect(found.sort()).toEqual(["/files/a.txt", "/files/sub/c.txt"].sort());

    found = dfs.findFilesWithReplicationFactor(3);
    expect(found).toEqual(["/files/b.txt"]);
  });

  test('should throw error when deleting non-existent file or directory', () => {
    expect(() => {
      dfs.delete("/nonexistent");
    }).toThrow();
  });

  test('should throw error when retrieving metadata for non-existent file', () => {
    expect(() => {
      dfs.getFileMetadata("/no/file.txt");
    }).toThrow();
  });

  test('should throw error when listing files in a non-existent directory', () => {
    expect(() => {
      dfs.listFiles("/unknown");
    }).toThrow();
  });

  test('should enforce correct path structures', () => {
    // Path must be absolute, should throw error if it does not begin with a /
    expect(() => {
      dfs.createDirectory("relative/path");
    }).toThrow();
    expect(() => {
      dfs.createFile("relative/file.txt", 2);
    }).toThrow();
    // Paths ending with a slash might be considered invalid as per spec.
    expect(() => {
      dfs.createDirectory("/invalid/");
    }).toThrow();
  });
});