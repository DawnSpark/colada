import { FileDto } from '../domain/file.dto'

class FileService {
 getFiles() : FileDto[] {
    return [
        new FileDto("daily-simple.conf", 1024*22, new Date('2020-12-17T18:56:15')),
        new FileDto("daily-asia.conf", 1024*23, new Date('2020-11-27T03:24:00')),
    ];
 }
}

export { FileService }