import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface DatasetResponse {
  datasets: string[];
}
@Injectable({
  providedIn: 'root'
})

export class DatasetsService {
  constructor(private http: HttpClient) {}

  getDatasets(){
    return this.http.get<DatasetResponse>('http://127.0.0.1:5000/api/datasets');
  }

  getDatasetFile(filename: string){
    return this.http.get(`http://127.0.0.1:5000/api/dataset/${filename}`, {responseType: 'json'});
  }

  sendQuery(filename: string, question: string) {
    const payload = { filename, question };
    return this.http.post<any>('http://127.0.0.1:5000/query', payload);
  }
}
